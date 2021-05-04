"""Utils functions"""

# System imports
import glob
import re
import sys


def is_function_decl(index, lines):
    """Check that the line is a function declaration"""

    line = lines[index]
    previous_line = lines[index - 1]
    types = ["char", "signed char", "unsigned char", "string", "short", "short int",
             "signed short", "signed short int", "unsigned short", "unsigned short int",
             "int", "signed", "signed int", "unsigned", "unsigned int", "long", "long int",
             "signed long", "signed long int", "unsigned long", "unsigned long int", "long long",
             "long long int", "signed long long", "signed long long int", "unsigned long long",
             "unsigned long long int", "float", "double", "long double", "struct", "bool", "void"]
    return_types = "".join([r"(?<=%s\s)|" % x for x in types])[:-1]
    previous_types = "".join(["%s|" % t for t in types])[:-1]

    return (re.search(r"\(", line) and
            re.search(r"^[^<;>]+$", line) and
            re.search(r"^[^<:>]+$", line) and
            not re.search(r"^\#", line) and
            not re.search(r"\(.*?\(", line) and
            not re.search(r"\=", line) and
            (re.search(r"(?<=%s).*?(?=\s?\()" % return_types, line) or
             re.search(r"((%s)\s*)$" % previous_types, previous_line)))


def collect_features(project_path):
    """Collect project features."""

    features = {}

    for filename in glob.iglob(project_path + '**/**', recursive=True):
        for extension in ['.c', '.cpp', '.cs']:
            if filename.endswith(extension):
                print("RUNNING", filename)

                function_flag = False

                try:
                    func_file = open(filename, "r").readlines()
                except:
                    continue

                for index, line in enumerate(func_file):
                    try:
                        if not function_flag and is_function_decl(index, func_file):
                            name = get_function_name(line)
                            if name == '' or re.search(r"^[\[|\]|{|}]", name):
                                continue

                            braces_stack = []
                            function_flag = True
                            parameters = get_parameters(index, func_file)

                        if function_flag:
                            exp = find_feature_exp(index, func_file)
                            if exp and exp not in ['0', '1']:
                                target_file = filename.split('repo/', 1)[1]
                                save_feature_exp(exp, target_file, name, parameters, features)

                            # Controls function scope
                            for copen in re.findall(r"{", line):
                                braces_stack.append(copen)
                            for cclose in re.findall(r"}", line):
                                braces_stack.pop()
                                if len(braces_stack) == 0:
                                    function_flag = False
                    except:
                        continue

    return features


def generate_model(features):
    """Generate feature model."""

    all_features = set()
    for filename, functions in features.items():
        for function, features in functions.items():
            for feature in features:
                for and_feature in feature.split(' AND'):
                    for or_feature in and_feature.split(' OR'):
                        final_feature = re.sub(r'NOT | NOT|\)|\(| ', '', or_feature)
                        if final_feature:
                            all_features.add(final_feature)

    model = {}
    for index, feature in enumerate(all_features):
        model.update({index+1: { "type": "Feature", "attr": "optional", "name": feature}})

    print("DONE")
    return model


def get_function_name(line):
    """Get name of a function."""

    func_name = re.split(r"\(", line)[0]
    func_name = re.split(r" ", func_name)[-1]
    func_name = re.sub(r"(\*|\+|\-)", r"", func_name)
    return func_name


def get_parameters(index, lines):
    """Get parameters of a function."""
    def transform_parameters(parameters):
        final_parameters = ""
        parameters_list = re.split(r", ", parameters)
        for parameter in parameters_list:
            var_name = re.split(r" ", parameter)[-1]
            var_name = re.escape(var_name)
            if re.search(r"\*", var_name):
                count_asterisks = len(re.findall(r"\*", var_name))
                asterisks = "".join([r"\*" for x in range(0, count_asterisks)])
                var_name = var_name.partition(asterisks)[-1]
                parameter = re.sub(r"%s$" % var_name, r"", parameter)
            else:
                parameter = re.sub(r" %s" % var_name, r"", parameter)
            final_parameters += "%s," % parameter
        return re.sub(r",$", r"", final_parameters)

    line = lines[index]
    parameters = line.partition("(")[-1]
    while not re.search(r"\)", parameters):
        index += 1
        if not lines[index].startswith("#"):
            parameters += lines[index]
    parameters = parameters.partition(")")[0]
    parameters = re.sub(r"\s+", r" ", parameters)
    parameters = re.sub(r"\+|\-", r"", parameters)
    return transform_parameters(parameters)


def find_feature_exp(index, lines):
    """Find expressions on the line"""
    line = lines[index]
    
    while line.rstrip().endswith('\\'):
        index += 1
        line += lines[index]

    line = line.split('/*')[0].split('//')[0]
    line = re.sub(r'\(', ' ( ', line)
    line = re.sub(r'\)', ' ) ', line)

    feature_exp = ""
    if re.search(r"^#ifdef", line):
        feature_exp = ' '.join(re.split('\s+', line)[1:])
    elif re.search(r"^#ifndef", line):
        feature_exp = ' '.join(re.split('\s+', line)[1:])
        feature_exp = f'NOT {feature_exp}'
    elif re.search(r"^#if", line) or re.search(r"^#elif", line):
        feature_exp = ' '.join(re.split('\s+', line)[1:])
        feature_exp = re.sub('defined', '', feature_exp)
        feature_exp = re.sub('IS_ENABLED', '', feature_exp)

    feature_exp = re.sub(r"<|>|=|!=|:|\*|\+|\-|\/|,", '', feature_exp)
    feature_exp = re.sub(r"\!", 'NOT ', feature_exp)
    feature_exp = re.sub(r"\&\&", 'AND', feature_exp)
    feature_exp = re.sub(r"\&", 'AND', feature_exp)
    feature_exp = re.sub(r"\|\|", 'OR', feature_exp)
    feature_exp = re.sub(r"\|", 'OR', feature_exp)
    feature_exp = re.sub(r"\\", '', feature_exp)

    temp_feature_exp = ''
    is_feature = False
    for split in feature_exp.split():
        try:
            temp = re.sub(r"x|L|df|fL|\(|\)", '', split)
            int(temp)
            if split.startswith("("):
                temp_feature_exp = f"({temp_feature_exp}"
            if split.endswith(")"):
                temp_feature_exp = f"{temp_feature_exp})"
            continue
        except ValueError:
            pass
        if split in ['NOT', 'AND', 'OR', '(NOT', '(AND', '(OR', '(', ')']:
            is_feature = False
        else:
            if is_feature:
                temp_feature_exp += "AND "
            is_feature = True
        temp_feature_exp += f"{split} "
    
    temp_feature_exp = re.sub(r'\( ', '(', temp_feature_exp)
    temp_feature_exp = re.sub(r' \)', ')', temp_feature_exp)
    temp_feature_exp = re.sub(r' NOT\)| AND\)| OR\)', ')', temp_feature_exp)
    temp_feature_exp = re.sub(r'\(\)', '', temp_feature_exp)

    final_feature_exp = ''
    for split in temp_feature_exp.split():
        if split.startswith("(") and split.endswith(")"):
            split = split[1:-1]
        final_feature_exp += f"{split} "

    final_feature_exp = ' '.join(final_feature_exp.split())
    if final_feature_exp.startswith("(") and final_feature_exp.endswith(")"):
        final_feature_exp = final_feature_exp[1:-1]

    final_feature_exp = re.sub(r' AND$| OR$', '', final_feature_exp)

    return ' '.join(final_feature_exp.split())


def save_feature_exp(feature_exp, target_file, target_function, target_parameters, features):
    """Save feature expression"""

    function = f"{target_function}({target_parameters})"

    features.setdefault(target_file, {})
    features[target_file].setdefault(function, [])
    if feature_exp not in features[target_file][function]:
        features[target_file][function].append(feature_exp)


def show_results(data):
    for strategy in ['one_enabled', 'one_disabled', 'most_enabled_disabled']:
        if strategy in data:
            print(f"{strategy}: {len(data[strategy])}")
