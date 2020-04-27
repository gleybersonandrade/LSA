"""Sampling functions"""

def one_enabled(data, features):
    """One Enabled sampling algorithm"""     
    data['one_enabled'] = []
    temp = {}
    for count, feature in enumerate(features, 1):
        temp['conf_' + str(count)] = []
        temp['conf_' + str(count)].append(feature)
    data['one_enabled'].append(temp)


def one_disabled(data, features):
    """One Disabled sampling algorithm"""
    data['one_disabled'] = []
    temp = {}
    for count in range(0, len(features)):
        features_temp = features.copy()
        del[features_temp[count]]
        temp['conf_' + str(count + 1)] = features_temp
    data['one_disabled'].append(temp)


def most_enabled_disabled(data, features):
    """Most Enabled Disabled sampling algorithm"""
    data['most_enabled_disabled'] = []
    temp = {}
    temp['conf_1'] = features
    temp['conf_2'] = [{}]
    data['most_enabled_disabled'].append(temp)
