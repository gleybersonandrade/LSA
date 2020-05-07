"""Sampling functions"""

# System imports
import random
import re
import sys
from random import randrange


def check(product, data):
    """Check if product does not exist in the data"""
    if type(data) == dict:
        data = data.values()
    for d in data:
        if product == d:
            return False
    return True


def get_all_features(features, data):
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
            data['one_enabled'].update({index: [feature]})

    def one_disabled():
        """One Disabled sampling algorithm"""
        data['one_disabled'] = {}
        for index, feature in enumerate(features):
            features_temp = features.copy()
            features_temp.remove(feature)
            data['one_disabled'].update({index: features_temp})

    def most_enabled_disabled():
        """Most Enabled Disabled sampling algorithm"""
        data['most_enabled_disabled'] = {}
        data['most_enabled_disabled'].update({"0": features})
        data['most_enabled_disabled'].update({"1": []})

    one_enabled()
    one_disabled()
    most_enabled_disabled()
    return data


def rand_original(model):
    """Create random original data"""

    features_data = {}
    get_all_features(model, features_data)

    data = {"features": features_data}    
    features = list(data["features"].keys())
    temp_products = []

    def one_enabled():
        """One Enabled sampling algorithm"""
        for index, feature in enumerate(features):
            temp_products.append([feature])

    def one_disabled():
        """One Disabled sampling algorithm"""
        for index, feature in enumerate(features):
            features_temp = features.copy()
            features_temp.remove(feature)
            temp_products.append(features_temp)

    def most_enabled_disabled():
        """Most Enabled Disabled sampling algorithm"""
        temp_products.append(features)
        temp_products.append([])

    one_enabled()
    one_disabled()
    most_enabled_disabled()

    data['rand'] = {}
    for index, product in enumerate(random.choices(temp_products, k=3)):
        data['rand'].update({index: product})

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
                data['one_enabled'].update({count: mandatory})
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
                data['one_disabled'].update({count: features_temp})
                count += 1

    def most_enabled_disabled():
        """Most Enabled Disabled sampling algorithm"""
        count = len(data['most_enabled_disabled'])
        if check([], data['most_enabled_disabled']):
            data['most_enabled_disabled'].update({count: []})
        if check(features, data['most_enabled_disabled']):
            data['most_enabled_disabled'].update({count+1: features})

    for strategy in ['one_enabled', 'one_disabled', 'most_enabled_disabled']:
        data[strategy] = {}
    one_enabled()
    one_disabled()
    most_enabled_disabled()
    return data


def rand_any(model):
    """Create random any data"""

    data = {"features": {}}
    temp_products = []

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

        for feature in features:
            mandatory = get_mandatory(feature)
            if check(mandatory, temp_products):
                temp_products.append(mandatory)

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

        for feature in features:
            attr = data["features"][feature]["attr"]
            if attr == "mandatory":
                continue
            features_copy = features.copy()
            children = get_children(feature)
            features_temp = [f for f in features_copy if f not in children]
            if check(features_temp, temp_products):
                temp_products.append(features_temp)

    def most_enabled_disabled():
        """Most Enabled Disabled sampling algorithm"""
        if check([], temp_products):
            temp_products.append([])
        if check(features, temp_products):
            temp_products.append(features)

    one_enabled()
    one_disabled()
    most_enabled_disabled()

    data['rand'] = {}
    for index, product in enumerate(random.choices(temp_products, k=3)):
        data['rand'].update({index: product})
    
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
                data['one_enabled'].update({count: mandatory})
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
                data['one_disabled'].update({count: features_temp})
                count += 1

    def most_enabled_disabled(features):
        """Most Enabled Disabled sampling algorithm"""
        count = len(data['most_enabled_disabled'])
        if check([], data['most_enabled_disabled']):
            data['most_enabled_disabled'].update({count: []})
        if check(features, data['most_enabled_disabled']):
            data['most_enabled_disabled'].update({count+1: features})

    for strategy in ['one_enabled', 'one_disabled', 'most_enabled_disabled']:
        data[strategy] = {}
    for b in blend:
        features = list(b.keys())
        one_enabled(features)
        one_disabled(features)
        most_enabled_disabled(features)

    return data


def rand_all(model):
    """Create random all data"""

    blend = []
    data = {"features": {}}
    get_all_features(model, data["features"])
    temp_products = []

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

        for feature in features:
            mandatory = get_mandatory(feature)
            if check(mandatory, temp_products):
                temp_products.append(mandatory)

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

        for feature in features:
            attr = data["features"][feature]["attr"]
            if attr == "mandatory":
                continue

            features_copy = features.copy()
            children = get_children(feature)
            features_temp = [f for f in features_copy if f not in children]
            if check(features_temp, temp_products):
                temp_products.append(features_temp)

    def most_enabled_disabled(features):
        """Most Enabled Disabled sampling algorithm"""
        if check([], temp_products):
            temp_products.append([])
        if check(features, temp_products):
            temp_products.append(features)

    for b in blend:
        features = list(b.keys())
        one_enabled(features)
        one_disabled(features)
        most_enabled_disabled(features)

    data['rand'] = {}
    for index, product in enumerate(random.choices(temp_products, k=3)):
        data['rand'].update({index: product})

    return data
