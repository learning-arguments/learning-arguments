from load_data import load_csv_data, bin_data_set, generate_case_model

bin_labels = ['very_low', 'low', 'medium', 'high', 'very_high']

if __name__ == "__main__":
    boston_housing_data_raw = load_csv_data('BostonHousing.csv')
    binned_data = bin_data_set(boston_housing_data_raw, bin_labels)
    case_model = generate_case_model(binned_data)
    print(case_model.valid)
