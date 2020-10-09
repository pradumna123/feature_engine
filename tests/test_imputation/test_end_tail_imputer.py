import pandas as pd
import pytest
from sklearn.exceptions import NotFittedError

from feature_engine.imputation import EndTailImputer


def test_automatically_find_variables_and_gaussian_imputation_on_right_tail(dataframe_na):
    # set up transformer
    imputer = EndTailImputer(imputation_method='gaussian', tail='right', fold=3, variables=None)
    X_transformed = imputer.fit_transform(dataframe_na)

    # set up expected output
    X_reference = dataframe_na.copy()
    X_reference['Age'] = X_reference['Age'].fillna(58.94908118478389)
    X_reference['Marks'] = X_reference['Marks'].fillna(1.3244261503263175)

    # test init params
    assert imputer.imputation_method == 'gaussian'
    assert imputer.tail == 'right'
    assert imputer.fold == 3
    assert imputer.variables == ['Age', 'Marks']
    # test fit attr
    assert imputer.input_shape_ == (8, 6)
    assert imputer.imputer_dict_ == {'Age': 58.94908118478389, 'Marks': 1.3244261503263175}
    # transform output: indicated vars ==> no NA, not indicated vars with NA
    assert X_transformed[['Age', 'Marks']].isnull().sum().sum() == 0
    assert X_transformed[['City', 'Name']].isnull().sum().sum() > 0
    pd.testing.assert_frame_equal(X_transformed, X_reference)


def test_user_enters_variables_and_iqr_imputation_on_right_tail(dataframe_na):
    # set up transformer
    imputer = EndTailImputer(imputation_method='iqr', tail='right', fold=1.5, variables=['Age', 'Marks'])
    X_transformed = imputer.fit_transform(dataframe_na)

    # set up expected result
    X_reference = dataframe_na.copy()
    X_reference['Age'] = X_reference['Age'].fillna(65.5)
    X_reference['Marks'] = X_reference['Marks'].fillna(1.0625)

    # test fit  and transform attr and output
    assert imputer.imputer_dict_ == {'Age': 65.5, 'Marks': 1.0625}
    assert X_transformed[['Age', 'Marks']].isnull().sum().sum() == 0
    pd.testing.assert_frame_equal(X_transformed, X_reference)


def test_user_enters_variables_and_max_value_imputation(dataframe_na):
    imputer = EndTailImputer(imputation_method='max', tail='right', fold=2, variables=['Age', 'Marks'])
    imputer.fit(dataframe_na)
    assert imputer.imputer_dict_ == {'Age': 82.0, 'Marks': 1.8}


def test_automatically_select_variables_and_gaussian_imputation_on_left_tail(dataframe_na):
    imputer = EndTailImputer(imputation_method='gaussian', tail='left', fold=3)
    imputer.fit(dataframe_na)
    assert imputer.imputer_dict_ == {'Age': -1.520509756212462, 'Marks': 0.04224051634034898}


def test_user_enters_variables_and_iqr_imputation_on_left_tail(dataframe_na):
    # test case 5: IQR + left tail
    imputer = EndTailImputer(imputation_method='iqr', tail='left', fold=1.5, variables=['Age', 'Marks'])
    imputer.fit(dataframe_na)
    assert imputer.imputer_dict_ == {'Age': -6.5, 'Marks': 0.36249999999999993}


def test_raises_error_when_imputation_method_is_not_permitted_value():
    with pytest.raises(ValueError):
        EndTailImputer(imputation_method='arbitrary')


def test_raises_error_when_tail_is_string():
    with pytest.raises(ValueError):
        EndTailImputer(tail='arbitrary')


def test_raises_error_when_fold_is_1():
    with pytest.raises(ValueError):
        EndTailImputer(fold=-1)


def test_non_fitted_error(dataframe_na):
    with pytest.raises(NotFittedError):
        imputer = EndTailImputer()
        imputer.transform(dataframe_na)