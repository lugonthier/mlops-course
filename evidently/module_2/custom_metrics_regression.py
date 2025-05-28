import pandas as pd
import numpy as np
from sklearn import datasets
from sklearn.metrics import explained_variance_score, max_error

from evidently import ColumnMapping
from evidently.base_metric import InputData
from evidently.metrics.custom_metric import CustomValueMetric
from evidently.report import Report
from evidently.renderers.html_widgets import WidgetSize

TARGET_COLUMN = 'target'
PREDICTION_COLUMN = 'prediction'
SAVE_TO_HTML = True

housing_data = datasets.fetch_california_housing(as_frame=True)
housing_df = housing_data.frame
housing_df.rename(columns={'MedHouseVal': TARGET_COLUMN}, inplace=True)

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

def explained_variance_custom_func(data: InputData) -> float:
    """Calcule le score de variance expliquée sur les données actuelles."""
    return explained_variance_score(
        data.current_data[data.column_mapping.target],
        data.current_data[data.column_mapping.prediction]
    )

def max_error_custom_func(data: InputData) -> float:
    """Calcule l'erreur maximale sur les données actuelles."""
    return max_error(
        data.current_data[data.column_mapping.target],
        data.current_data[data.column_mapping.prediction]
    )


custom_metrics_report = Report(metrics=[
    CustomValueMetric(
        func=explained_variance_custom_func,
        title="Custom: Explained Variance Score (Current)",
        size=WidgetSize.HALF
    ),
    CustomValueMetric(
        func=max_error_custom_func,
        title="Custom: Max Error (Current)",
        size=WidgetSize.HALF
    )
])

custom_metrics_report.run(
    reference_data=housing_ref,
    current_data=housing_cur,
    column_mapping=regression_column_mapping
)


if SAVE_TO_HTML:
    report_file_path_custom_reg = "evidently_custom_metrics_regression_report.html"
    custom_metrics_report.save_html(report_file_path_custom_reg)
    print(f"Rapport avec métriques personnalisées sauvegardé dans : {report_file_path_custom_reg}")
