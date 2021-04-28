"""Sampling functions"""

# System imports
import json
import os
import random
import re


def check(product, data):
    """Check if product does not exist in the data"""

    if type(data) == dict:
        data = data.values()
    for d in data:
        if product == d:
            return False
    return True


def get_all_features(features, data):
    """Return all features from data"""

    for fid, feature in features.items():
        if feature["type"] == "Feature":
            data.update({fid: {"name": feature["name"],
                               "attr": feature["attr"]}})
        children = feature.get("children", {})
        get_all_features(children, data)


def original(model):
    """Create original data"""

    features_data = {}
    get_all_features(model, features_data)

    data = {"features": features_data}
    features = list(data["features"].keys())

    def one_enabled():
        """One Enabled sampling algorithm"""
        data['one_enabled'] = {}
        for index, feature in enumerate(features):
            data['one_enabled'].update({index+1: [feature]})

    def one_disabled():
        """One Disabled sampling algorithm"""
        data['one_disabled'] = {}
        for index, feature in enumerate(features):
            features_temp = features.copy()
            features_temp.remove(feature)
            data['one_disabled'].update({index+1: features_temp})

    def most_enabled_disabled():
        """Most Enabled Disabled sampling algorithm"""
        data['most_enabled_disabled'] = {}
        data['most_enabled_disabled'].update({"1": features})
        data['most_enabled_disabled'].update({"2": []})

    one_enabled()
    one_disabled()
    most_enabled_disabled()
    return data


def rand_original(model):
    """Create random original data"""

    original_data = original(model)

    temp_products = []
    for strategy in ['one_enabled', 'one_disabled', 'most_enabled_disabled']:
        for product in original_data[strategy].values():
            temp_products.append(product)

    data = {
        'features': original_data['features'],
        'rand': {}
    }
    for index, product in enumerate(random.choices(temp_products, k=3)):
        data['rand'].update({index+1: product})

    return data


def any(model):
    """Create any data"""

    data = {"features": {}}

    def get_features(features):
        for fid, feature in features.items():
            children = feature.get("children", {})
            if feature["type"] == "Feature":
                data["features"].update({fid: {"name": feature["name"],
                                               "attr": feature["attr"]}})
            elif feature["type"] == "Group" and feature["attr"] == "AND":
                target = random.choice(list(children.keys()))
                children = {target: children[target]}
            get_features(children)

    get_features(model)
    features = list(data["features"].keys())

    def one_enabled():
        """One Enabled sampling algorithm"""
        def get_mandatory(fid):
            mandatory = []
            for feature in features:
                attr = data["features"][feature]["attr"]
                prefix = feature[:-2]
                if (re.match(feature, fid) or
                   (attr == "mandatory" and prefix in mandatory)):
                    mandatory.append(feature)

            return mandatory

        count = len(data['one_enabled'])
        for feature in features:
            mandatory = get_mandatory(feature)
            if check(mandatory, data['one_enabled']):
                data['one_enabled'].update({count+1: mandatory})
                count += 1

    def one_disabled():
        """One Disabled sampling algorithm"""
        def get_children(fid):
            children = []
            for feature in features:
                attr = data["features"][feature]["attr"]
                prefix = feature[:-2]
                if re.match(fid, feature) or (prefix in children and
                                              attr == "mandatory"):
                    children.append(feature)

            return children

        count = len(data['one_disabled'])
        for feature in features:
            attr = data["features"][feature]["attr"]
            if attr == "mandatory":
                continue
            features_copy = features.copy()
            children = get_children(feature)
            features_temp = [f for f in features_copy if f not in children]
            if check(features_temp, data['one_disabled']):
                data['one_disabled'].update({count+1: features_temp})
                count += 1

    def most_enabled_disabled():
        """Most Enabled Disabled sampling algorithm"""
        if check([], data['most_enabled_disabled']):
            data['most_enabled_disabled'].update({len(data['most_enabled_disabled'])+1: []})
        if check(features, data['most_enabled_disabled']):
            data['most_enabled_disabled'].update({len(data['most_enabled_disabled'])+1: features})

    for strategy in ['one_enabled', 'one_disabled', 'most_enabled_disabled']:
        data[strategy] = {}
    one_enabled()
    one_disabled()
    most_enabled_disabled()
    return data


def rand_any(model):
    """Create random any data"""

    any_data = any(model)

    temp_products = []
    for strategy in ['one_enabled', 'one_disabled', 'most_enabled_disabled']:
        for product in any_data[strategy].values():
            temp_products.append(product)

    data = {
        'features': any_data['features'],
        'rand': {}
    }
    for index, product in enumerate(random.choices(temp_products, k=3)):
        data['rand'].update({index+1: product})

    return data


def all(model):
    """Create all data"""

    blend = []
    data = {"features": {}}
    get_all_features(model, data["features"])

    def get_features(features, features_data):
        for fid, feature in features.items():
            if feature["type"] == "Group" and feature["attr"] == "AND":
                continue
            if feature["type"] == "Feature":
                features_data.update({fid: {"name": feature["name"],
                                               "attr": feature["attr"]}})
            children = feature.get("children", {})
            get_features(children, features_data)

    def get_blend(features, base, flag=False):
        child_data = {}
        for fid, feature in features.items():
            children = feature.get("children", {})
            if feature["type"] == "Group" and feature["attr"] == "AND":
                for cid, child in children.items():
                    temp = base.copy()
                    temp.update({cid: {"name": child["name"],
                                       "attr": child["attr"]}})
                    temp.update(get_blend({cid: child}, temp, True))
                    blend.append(temp)
            elif flag and feature["type"] == "Feature":
                child_data.update({fid: {"name": feature["name"],
                                         "attr": feature["attr"]}})
            child_data.update(get_blend(children, base, flag))
        return child_data

    features_data = {}
    get_features(model, features_data)
    get_blend(model, features_data)

    def one_enabled(features):
        """One Enabled sampling algorithm"""
        def get_mandatory(fid):
            mandatory = []
            for feature in features:
                attr = data["features"][feature]["attr"]
                prefix = feature[:-2]
                if (re.match(feature, fid) or
                   (attr == "mandatory" and prefix in mandatory)):
                    mandatory.append(feature)

            return mandatory

        count = len(data['one_enabled'])
        for feature in features:
            mandatory = get_mandatory(feature)
            if check(mandatory, data['one_enabled']):
                data['one_enabled'].update({count+1: mandatory})
                count += 1

    def one_disabled(features):
        """One Disabled sampling algorithm"""
        def get_children(fid):
            children = []
            for feature in features:                
                attr = data["features"][feature]["attr"]
                prefix = feature[:-2]
                if re.match(fid, feature) or (prefix in children and
                                              attr == "mandatory"):
                    children.append(feature)

            return children

        count = len(data['one_disabled'])
        for feature in features:
            attr = data["features"][feature]["attr"]
            if attr == "mandatory":
                continue

            features_copy = features.copy()
            children = get_children(feature)
            features_temp = [f for f in features_copy if f not in children]
            if check(features_temp, data['one_disabled']):
                data['one_disabled'].update({count+1: features_temp})
                count += 1

    def most_enabled_disabled(features):
        """Most Enabled Disabled sampling algorithm"""
        if check([], data['most_enabled_disabled']):
            data['most_enabled_disabled'].update({len(data['most_enabled_disabled'])+1: []})
        if check(features, data['most_enabled_disabled']):
            data['most_enabled_disabled'].update({len(data['most_enabled_disabled'])+1: features})

    for strategy in ['one_enabled', 'one_disabled', 'most_enabled_disabled']:
        data[strategy] = {}
    if blend:
        for b in blend:
            features = list(b.keys())
            one_enabled(features)
            one_disabled(features)
            most_enabled_disabled(features)
    else:
        features = list(features_data.keys())
        one_enabled(features)
        one_disabled(features)
        most_enabled_disabled(features)

    return data


def rand_all(model):
    """Create random all data"""

    all_data = all(model)

    temp_products = []
    for strategy in ['one_enabled', 'one_disabled', 'most_enabled_disabled']:
        for product in all_data[strategy].values():
            temp_products.append(product)

    data = {
        'features': all_data['features'],
        'rand': {}
    }
    for index, product in enumerate(random.choices(temp_products, k=3)):
        data['rand'].update({index+1: product})

    return data
