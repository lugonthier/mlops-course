
from evidently.metrics import (
    ColumnDriftMetric,

)

from evidently.ui.dashboards import CounterAgg
from evidently.ui.dashboards import DashboardPanelCounter
from evidently.ui.dashboards import DashboardPanelPlot
from evidently.ui.dashboards import PanelValue
from evidently.ui.dashboards import PlotType
from evidently.ui.dashboards import ReportFilter
from evidently.ui.dashboards import DashboardPanelTestSuite

from evidently.ui.dashboards import TestSuitePanelType
from evidently.renderers.html_widgets import WidgetSize
from evidently.ui.workspace import Workspace
from evidently.ui.workspace import WorkspaceBase
from evidently.ui.remote import RemoteWorkspace

YOUR_PROJECT_NAME = "PROJECT_NAME"
YOUR_PROJECT_DESCRIPTION = "Test project using Churn dataset"

def create_project(workspace: WorkspaceBase):
    project = workspace.create_project(YOUR_PROJECT_NAME)
    project.dashboard.add_panel(
                DashboardPanelCounter(
            filter=ReportFilter(metadata_values={}, tag_values=["data_drift"]),
            agg=CounterAgg.NONE,
            title="Churn Dataset",
        )
    )
        ## Data Quality & Stability
    project.dashboard.add_panel(
        DashboardPanelTestSuite(
            title="Data Stability tests",
            filter=ReportFilter(metadata_values={}, tag_values=["data_quality_test_suite"], include_test_suites=True),
            size=WidgetSize.HALF
        )
    )
    

    project.dashboard.add_panel(
        DashboardPanelTestSuite(
            title="Data Stability tests: detailed",
            filter=ReportFilter(metadata_values={}, tag_values=["data_quality_test_suite"], include_test_suites=True),
            size=WidgetSize.HALF,
            panel_type=TestSuitePanelType.DETAILED

        )
    )
        
        
    ### Data Drift tests
    project.dashboard.add_panel(
        DashboardPanelTestSuite(
            title="Data Drift tests",
            filter=ReportFilter(metadata_values={}, tag_values=["data_drift_test_suite"], include_test_suites=True),
            size=WidgetSize.HALF
        )
    )
    

    project.dashboard.add_panel(
        DashboardPanelTestSuite(
            title="Data Drift tests: detailed",
            filter=ReportFilter(metadata_values={}, tag_values=["data_drift_test_suite"], include_test_suites=True),
            size=WidgetSize.HALF,
            panel_type=TestSuitePanelType.DETAILED

        )
    )
        
     ### Data Drift
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Dataset Drift",
            filter=ReportFilter(metadata_values={}, tag_values=["data_drift"]),
            values=[
                PanelValue(
                    metric_id="DatasetDriftMetric",
                    field_path="share_of_drifted_columns",
                    legend="Drift Share",
                ),
            ],
            plot_type=PlotType.BAR,
            size=WidgetSize.HALF,
        )
    )
    
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Prediction Drift",
            filter=ReportFilter(metadata_values={}, tag_values=["prediction_drift"]),
            values=[
                PanelValue(
                    metric_id="ColumnDriftMetric",
                    metric_args={"column_name.name": "prediction"},
                    field_path=ColumnDriftMetric.fields.drift_score,
                    legend="prediction",
                ),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )
    
        
    ### Target Drift & Model Performance
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Target Drift",
            filter=ReportFilter(metadata_values={}, tag_values=["target_drift"]),
            values=[
                PanelValue(
                    metric_id="ColumnDriftMetric",
                    metric_args={"column_name.name": "Churn"},
                    field_path=ColumnDriftMetric.fields.drift_score,
                    legend="target: Churn",
                ),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )


    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Model Performance",
            filter=ReportFilter(metadata_values={}, tag_values=["model_performance"]),
            values=[
                PanelValue(metric_id="ClassificationQualityMetric", field_path="reference.accuracy", legend="reference accuracy"),
                PanelValue(metric_id="ClassificationQualityMetric", field_path="current.accuracy", legend="current accuracy"),
                PanelValue(metric_id="ClassificationQualityMetric", field_path="reference.f1", legend="reference f1"),
                PanelValue(metric_id="ClassificationQualityMetric", field_path="current.f1", legend="current f1"),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF
        )
    )
    
    project.save()
    return project
    
if __name__ == "__main__":
    ws = RemoteWorkspace("https://evidently-server-instance-988498511057.europe-west9.run.app")
    create_project(ws)