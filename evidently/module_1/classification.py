from sklearn import datasets
from sklearn import ensemble

from evidently.report import Report
from evidently.metric_preset import ClassificationPreset
from evidently.metrics import (
    ClassificationQualityMetric,
    ClassificationClassBalance,
    ConflictTargetMetric,
    ConflictPredictionMetric,
    ClassificationConfusionMatrix,
    ClassificationQualityByClass,
    ClassificationClassSeparationPlot,
    ClassificationProbDistribution,
    ClassificationRocCurve,
    ClassificationPRCurve,
    ClassificationPRTable,
    ClassificationQualityByFeatureTable,
)

TARGET_COLUMN = "target"
PREDICTION_COLUMN = "prediction"
SAVE_TO_HTML = True

bcancer_data = datasets.load_breast_cancer(as_frame=True)
bcancer_df = bcancer_data.frame
feature_names = bcancer_data.feature_names.tolist()


bcancer_ref = bcancer_df.sample(n=300, random_state=42)

bcancer_cur = bcancer_df.drop(bcancer_ref.index).sample(n=200, random_state=42)


model = ensemble.RandomForestClassifier(random_state=1, n_estimators=5, max_depth=3)
model.fit(bcancer_ref[feature_names], bcancer_ref[TARGET_COLUMN])

bcancer_ref[PREDICTION_COLUMN] = model.predict_proba(bcancer_ref[feature_names])[:, 1]
bcancer_cur[PREDICTION_COLUMN] = model.predict_proba(bcancer_cur[feature_names])[:, 1]

### With Preset ###
classification_performance_report = Report(
    metrics=[
        ClassificationPreset(probas_threshold=0.7),
    ],
)

classification_performance_report.run(
    reference_data=bcancer_ref,
    current_data=bcancer_cur,
)

if SAVE_TO_HTML:
    report_file_path_preset = "evidently_preset_classification_report.html"
    classification_performance_report.save_html(report_file_path_preset)

### Without Preset ###
quality_by_feature_cols = feature_names[:3]
detailed_classification_report = Report(
    metrics=[
        ClassificationQualityMetric(),
        ClassificationClassBalance(),
        ConflictTargetMetric(),
        ConflictPredictionMetric(),
        ClassificationConfusionMatrix(),
        ClassificationQualityByClass(),
        ClassificationClassSeparationPlot(),
        ClassificationProbDistribution(),
        ClassificationRocCurve(),
        ClassificationPRCurve(),
        ClassificationPRTable(),
        ClassificationQualityByFeatureTable(columns=quality_by_feature_cols),
        
    ]
)

detailed_classification_report.run(reference_data=bcancer_ref, current_data=bcancer_cur)

if SAVE_TO_HTML:
    report_file_path_detailed = "evidently_detailed_classification_report.html"
    detailed_classification_report.save_html(report_file_path_detailed)
