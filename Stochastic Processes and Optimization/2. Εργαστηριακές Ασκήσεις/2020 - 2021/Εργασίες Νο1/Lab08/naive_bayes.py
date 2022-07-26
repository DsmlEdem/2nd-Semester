problematic1 = open("problematic_valid.txt", "w")
problematic2 = open("problematic_invalid.txt", "w")

def load_file(file_name):
    fd = open(file_name, "r")
    my_set = set()
    for prefix in fd:
        prefix = prefix.rstrip()
        my_set.add(prefix)
    return my_set

def calculate_probabilities(dataset):
    stats = dict()
    for index in range(0, 7):
        stats[index] = dict()
    for prefix in dataset:
        features = handle_name(prefix)
        for index in range(0, 7):
            try:
                stats[index][features[index]] += 1
            except:
                stats[index][features[index]] = 1

    dataset_size = len(dataset)    
    for index in range(0, 7):
        for key in stats[index]:
            stats[index][key] /= dataset_size
    return stats

def handle_name(prefix):
    total_length = len(prefix)
    total_digits, max_numeric_sequence = numeric(prefix)
    total_consonants, max_consonants_sequence = consonants(prefix)
    total_vowels, max_vowels_sequence = vowels(prefix)
    return total_length, total_digits, max_numeric_sequence, total_consonants, max_consonants_sequence, total_vowels, max_vowels_sequence

def vowels(prefix):
    total_vowels = 0
    vowels_sequence = list()
    current_sequence = 0
    for char in prefix:
        if char == 'a' or char == 'e' or char == 'i' or char == 'o' or char == 'u':
            total_vowels += 1
            current_sequence += 1
        else:
            vowels_sequence.append(current_sequence)
            current_sequence = 0
    vowels_sequence.append(current_sequence)
    max_vowels_sequence = max(vowels_sequence)
    return total_vowels, max_vowels_sequence

def consonants(prefix):
    total_consonants = 0
    consonants_sequence = list()
    current_sequence = 0
    for char in prefix:
        if char != 'a' and char != 'e' and char != 'i' and char != 'o' and char != 'u' and char != '-' and char.isdigit() == False:
            total_consonants += 1
            current_sequence += 1
        else:
            consonants_sequence.append(current_sequence)
            current_sequence = 0
    consonants_sequence.append(current_sequence)
    max_consonants_sequence = max(consonants_sequence)
    return total_consonants, max_consonants_sequence

def numeric(prefix):
    total_digits = 0
    numeric_sequence = list()
    current_sequence = 0
    for char in prefix:
        if char.isdigit() == True:
            total_digits += 1
            current_sequence += 1
        else:
            numeric_sequence.append(current_sequence)
            current_sequence = 0
    numeric_sequence.append(current_sequence)
    max_numeric_sequence = max(numeric_sequence)
    return total_digits, max_numeric_sequence
            
def find_prob(prefix, stats, fd):
    tl, td, mns, tc, mcs, tv, mvs = handle_name(prefix)
    try:
        prob = stats[0][tl] * stats[1][td] * stats[2][mns] * stats[3][tc] * stats[4][mcs] * stats[5][tv] * stats[6][mvs]
    except:
        prob = 0
        fd.write(prefix + "\n")
    return prob

def apply_on_test_set(test_set, category, valid_stats, invalid_stats, fd):
    misclassifications = 0
    names_processed = 0
    for prefix in test_set:
        valid_prob = find_prob(prefix, valid_stats, fd)
        invalid_prob = find_prob(prefix, invalid_stats, fd)
        if valid_prob != 0 and invalid_prob != 0:
            names_processed += 1
            if category == "valid" and valid_prob < invalid_prob:
                misclassifications += 1
            elif category == "invalid" and valid_prob > invalid_prob:
                misclassifications += 1
    return misclassifications, names_processed

if __name__ == "__main__":
    # Load valid names training set
    valid_names_training = load_file("./valid_training.txt")
    # Load valid names test set
    valid_names_test = load_file("./valid_test.txt")
    # Load invalid names training set
    invalid_names_training = load_file("./invalid_training.txt")
    # Load invalid names test set
    invalid_names_test = load_file("./invalid_test.txt") 

    valid_stats = calculate_probabilities(valid_names_training)
    invalid_stats = calculate_probabilities(invalid_names_training)

    valid_misclassifications, valid_names_processed = apply_on_test_set(valid_names_test, "valid", valid_stats, invalid_stats, problematic1)
    invalid_misclassifications, invalid_names_processed = apply_on_test_set(invalid_names_test, "invalid", valid_stats, invalid_stats, problematic2)

    print("Valid names misclassified as invalid - Ratio: ", (valid_misclassifications / valid_names_processed) * 100)
    print("Invalid names misclassified as valid - Ratio: ", (invalid_misclassifications / invalid_names_processed) * 100)