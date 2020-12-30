# -*- encoding: utf-8 -*-
# @Time    :   2020/12/10
# @Author  :   Xiaolei Wang
# @email   :   wxl1999@foxmail.com

# UPDATE
# @Time    :   2020/12/20, 2020/12/15
# @Author  :   Xiaolei Wang, Yuanhang Zhou
# @email   :   wxl1999@foxmail.com, sdzyh002@gmail

from copy import copy
from typing import List, Union, Optional

import torch


def add_start_end_token_idx(vec: list, start_token_idx=None, end_token_idx=None):
    res = copy(vec)
    if start_token_idx:
        res.insert(0, start_token_idx)
    if end_token_idx:
        res.append(end_token_idx)
    return res


def padded_tensor(
        items: List[Union[List[int], torch.LongTensor]],
        pad_idx: int = 0,
        pad_tail: bool = True,
        max_len: Optional[int] = None,
) -> torch.LongTensor:
    """
    Create a padded matrix from an uneven list of lists.

    Returns padded matrix.

    Matrix is right-padded (filled to the right) by default, but can be
    left padded if the flag is set to True.

    Matrix can also be placed on cuda automatically.

    :param list[iter[int]] items: List of items
    :param int pad_idx: the value to use for padding
    :param bool pad_tail:
    :param int max_len: if None, the max length is the maximum item length

    :returns: padded
    :rtype: (Tensor[int64], list[int])
    """

    # number of items
    n = len(items)
    # length of each item
    lens: List[int] = [len(item) for item in items]  # type: ignore
    # max in time dimension
    t = max(lens) if max_len is None else max_len
    # if input tensors are empty, we should expand to nulls
    t = max(t, 1)

    if isinstance(items[0], torch.Tensor):
        # keep type of input tensors, they may already be cuda ones
        output = items[0].new(n, t)  # type: ignore
    else:
        output = torch.LongTensor(n, t)  # type: ignore
    output.fill_(pad_idx)

    for i, (item, length) in enumerate(zip(items, lens)):
        if length == 0:
            # skip empty items
            continue
        if not isinstance(item, torch.Tensor):
            # put non-tensors into a tensor
            item = torch.tensor(item, dtype=torch.long)  # type: ignore
        if pad_tail:
            # place at beginning
            output[i, :length] = item
        else:
            # place at end
            output[i, t - length:] = item

    return output


def get_onehot(data_list, categories) -> torch.Tensor:
    """transform lists of label into one-hot

    Args:
        data_list (list of list of int):
        categories (int): #label class

    Returns:
        torch.Tensor: onehot labels
    """
    onehot_labels = []
    for label_list in data_list:
        onehot_label = torch.zeros(categories)
        for label in label_list:
            onehot_label[label] = 1.0 / len(label_list)
        onehot_labels.append(onehot_label)
    return torch.stack(onehot_labels, dim=0)


def truncate(vec, max_length, truncate_tail=True):
    """truncate vec to make its length within max length

    Args:
        vec (list):
        max_length (int):
        truncate_tail (bool, optional): Defaults to True.

    Returns:
        list: truncated vec
    """
    if max_length is None:
        return vec
    if len(vec) <= max_length:
        return vec
    if truncate_tail:
        return vec[:max_length]
    else:
        return vec[-max_length:]


def merge_utt(conv, split_token_idx=None, split_in_tail=False, final_token_idx=None):
    """merge utterances in one conversation

    Args:
        conv (list of list of int): conversation consist of utterances consist of tokens

    Returns:
        list: tokens of all utterances in one conversation
    """
    merged_conv = []
    for utt in conv:
        for token in utt:
            merged_conv.append(token)
        if split_token_idx:
            merged_conv.append(split_token_idx)
    if split_token_idx and not split_in_tail:
        merged_conv = merged_conv[:-1]
    if final_token_idx:
        merged_conv.append(final_token_idx)
    return merged_conv
