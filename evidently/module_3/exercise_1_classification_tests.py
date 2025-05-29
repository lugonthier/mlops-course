from sklearn import datasets
from sklearn import ensemble

from evidently.tests import (
    TestAccuracyScore,
    TestColumnNumberOfMissingValues,
    TestPrecisionByClass,
    TestRecallByClass,
    TestF1ByClass,
    TestMostCommonValueShare,
    TestNumberOfColumns,
)
from evidently.test_suite import TestSuite
from evidently import ColumnMapping

TARGET_COLUMN = "target"
PREDICTION_COLUMN = "prediction" 
BINARY_PREDICTION_COLUMN = (
    "binary_prediction"  
)
SAVE_TO_HTML = True


bcancer_data = datasets.load_breast_cancer(as_frame=True)
bcancer_df = bcancer_data.frame
feature_names = bcancer_data.feature_names.tolist()

bcancer_ref = bcancer_df.sample(n=300, random_state=42)
bcancer_cur = bcancer_df.drop(bcancer_ref.index).sample(n=200, random_state=42)

model = ensemble.RandomForestClassifier(random_state=1, n_estimators=10, max_depth=5)
model.fit(bcancer_ref[feature_names], bcancer_ref[TARGET_COLUMN])

bcancer_ref[PREDICTION_COLUMN] = model.predict_proba(bcancer_ref[feature_names])[:, 1]
bcancer_cur[PREDICTION_COLUMN] = model.predict_proba(bcancer_cur[feature_names])[:, 1]

threshold = 0.5
bcancer_ref[BINARY_PREDICTION_COLUMN] = (
    bcancer_ref[PREDICTION_COLUMN] >= threshold
).astype(int)
bcancer_cur[BINARY_PREDICTION_COLUMN] = (
    bcancer_cur[PREDICTION_COLUMN] >= threshold
).astype(int)


column_mapping = ColumnMapping()
column_mapping.target = TARGET_COLUMN
column_mapping.prediction = PREDICTION_COLUMN

binary_column_mapping = ColumnMapping()
binary_column_mapping.target = TARGET_COLUMN
binary_column_mapping.prediction = PREDICTION_COLUMN
binary_column_mapping.numerical_features = feature_names




classification_test_suite = TestSuite(
    tests=[

        TestAccuracyScore(gte=0.85), 
        TestPrecisionByClass(label=0, gte=0.80), 
        TestRecallByClass(label=0, gte=0.80), 
        TestF1ByClass(label=0, gte=0.80), 
        TestPrecisionByClass(label=1, gte=0.80), 
        TestRecallByClass(label=1, gte=0.80), 
        TestF1ByClass(label=1, gte=0.80), 
        TestColumnNumberOfMissingValues(
            column_name=TARGET_COLUMN, eq=0
        ), 
        TestColumnNumberOfMissingValues(
            column_name=BINARY_PREDICTION_COLUMN, eq=0
        ), 
        TestMostCommonValueShare(
            column_name=TARGET_COLUMN, lte=0.7
        ), 
        TestNumberOfColumns(
            eq=len(bcancer_df.columns) + 2
        ), 
    ]
)

classification_test_suite.run(
    current_data=bcancer_cur,
    reference_data=bcancer_ref,
    column_mapping=binary_column_mapping,
)

if SAVE_TO_HTML:
    report_file_path_tests = "evidently_classification_with_tests_report.html"
    classification_test_suite.save_html(report_file_path_tests)
    print(f"Test suite report saved to {report_file_path_tests}")
