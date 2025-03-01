from pprint import pprint
from falx.table.language import HOLE


def disable_sketch(p, new_vals, has_sep, comp_without_new_val):
    """check if the program sketch is a bad sketch, 
            we will prevent bad sketch directly 
    Args:
        p: program sketch in ast form
        new_vals: new values from the output, use to infer whether the output table contain new value comparing to the input
            (this helps deterimin if we should use operators that generates new value)
        has_sep: whethre the input table contains any value that can be applied to a separator
    Returns:
        True if the sketch should be disabled
        False (we'll keep the sketch)
    """

    def get_op_list(_ast):
        return [_ast["op"]] + [v for c in _ast["children"] if c["type"] == "node" for v in get_op_list(c)]

    ast = p.to_dict()
    op_list = get_op_list(ast)

    if len([x for x in new_vals if isinstance(x, (int, float, complex))]) == 0:
        # if output contains no new numerical values, we'll not use operaters generates new values
        if (comp_without_new_val == False) and "mutate" in op_list or "mutate_custom" in op_list or "cumsum" in op_list or "group_sum" in op_list:
            return True

    if len([x for x in new_vals if isinstance(x, (int, float, complex))]) > 0:
        # must use a operator if involves new value
        if not ("mutate" in op_list or "mutate_custom" in op_list or "cumsum" in op_list or "group_sum" in op_list):
            return True

    if has_sep is False and "separate" in op_list:
        return True

    if "select" in op_list or "filter" in op_list:
        # filter is currently disabled
        # select is implicitly used in visualization spec
        return True

    # group_sum and mutate_custom can only be used in the last operator
    if "group_sum" in op_list[1:] or "mutate_custom" in op_list[1:]:# or "cumsum" in op_list[1:]: 
        return True
    
    # No more than 1 gather, no more than 1 mutate
    if len([s for s in op_list if s in ["gather", "gather_neg"]]) > 1:
        return True
    if len([s for s in op_list if s in ["mutate", "mutate_custom"]]) > 1:
        return True

    def contains_repetition(_ast, except_list):
        """check if there is a sketch that contains repetitive components """
        for child in _ast["children"]:
            if child["type"] == "node": 
                if (child["op"] == _ast["op"] and child["op"] not in except_list) or contains_repetition(child, except_list):
                    return True
        return False

    # No repetitive component except for separate.
    if contains_repetition(ast, except_list=["separate"]): return True

    return False