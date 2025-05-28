import numpy as np
from sklearn import datasets
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import RegressionPreset
from evidently.metrics import (
    RegressionQualityMetric,
    RegressionPredictedVsActualScatter,
    RegressionPredictedVsActualPlot,
    RegressionErrorPlot,
    RegressionAbsPercentageErrorPlot,
    RegressionErrorDistribution,
    RegressionErrorNormality,
    RegressionTopErrorMetric,
    RegressionErrorBiasTable
)

TARGET_COLUMN = 'target'
PREDICTION_COLUMN = 'prediction'
SAVE_TO_HTML = True

housing_data = datasets.fetch_california_housing(as_frame=True)
housing_df = housing_data.frame
housing_df.rename(columns={'MedHouseVal': TARGET_COLUMN}, inplace=True)
feature_names = housing_data.feature_names

housing_ref = housing_df.sample(n=5000, random_state=42)
housing_cur = housing_df.drop(housing_ref.index).sample(n=5000, random_state=123)


np.random.seed(42) 

housing_ref[PREDICTION_COLUMN] = housing_ref[TARGET_COLUMN].values + np.random.normal(0, 0.5, housing_ref.shape[0])

housing_cur[PREDICTION_COLUMN] = housing_cur[TARGET_COLUMN].values + np.random.normal(0.1, 0.6, housing_cur.shape[0])

housing_ref.sort_index(inplace=True)
housing_cur.sort_index(inplace=True)

regression_column_mapping = ColumnMapping()
regression_column_mapping.target = TARGET_COLUMN
regression_column_mapping.prediction = PREDICTION_COLUMN


### With Preset ###
regression_performance_report = Report(metrics=[
    RegressionPreset(),
])

regression_performance_report.run(reference_data=housing_ref,
                                  current_data=housing_cur,
                                  column_mapping=regression_column_mapping)

if SAVE_TO_HTML:
    report_file_path_preset_reg = "evidently_preset_regression_performance_report.html"
    regression_performance_report.save_html(report_file_path_preset_reg)


### Without Preset ###
error_bias_cols = feature_names[:2]

detailed_regression_report = Report(metrics=[
    RegressionQualityMetric(),
    RegressionPredictedVsActualScatter(),
    RegressionPredictedVsActualPlot(),
    RegressionErrorPlot(),
    RegressionAbsPercentageErrorPlot(),
    RegressionErrorDistribution(),
    RegressionErrorNormality(),
    RegressionTopErrorMetric(),
    RegressionErrorBiasTable(columns=error_bias_cols)
])

detailed_regression_report.run(reference_data=housing_ref,
                             current_data=housing_cur,
                             column_mapping=regression_column_mapping)

if SAVE_TO_HTML:
    report_file_path_detailed_reg = "evidently_detailed_regression_report.html"
    detailed_regression_report.save_html(report_file_path_detailed_reg)
