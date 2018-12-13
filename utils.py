"""Sampling functions"""

def one_enabled(data, features):
    """One Enabled sampling algorithm"""     
    data['one_enabled'] = []
    temp = {}
    for count, feature in enumerate(features, 1):
        temp['configuration' + str(count)] = []
        temp['configuration' + str(count)].append(feature)
    data['one_enabled'].append(temp)

def one_disabled(data, features):
    """One Disabled sampling algorithm"""
    data['one_disabled'] = []
    temp = {}
    for count in range(0, len(features)):
        features_temp = features.copy()
        del[features_temp[count]]
        temp['configuration' + str(count + 1)] = features_temp
    data['one_disabled'].append(temp)

def most_enabled_disabled(data, features):
    """Most Enabled Disabled sampling algorithm"""
    data['most_enabled_disabled'] = []
    temp = {}
    temp['configuration1'] = features
    temp['configuration2'] = [{}]
    data['most_enabled_disabled'].append(temp)