import datetime

import numpy as np
import pandas as pd
import seaborn as sns
import pickle
import tempfile
import os
import statsmodels.api as sm
import jupyter # from sam
import nbformat # from sam

from shiny import ui, render, reactive, Inputs, Outputs, Session, App
from shiny.plotutils import brushed_points

nav = ui.layout_sidebar(
    ui.panel_sidebar(
        ui.input_select("format", "Output Format", choices={"html": "HTML",
                                                            "pdf": "pdf",
                                                            "pptx": "Powerpoint"}),
        ui.download_button("download_report", "Download Report")
    ),
    ui.panel_main(
        ui.output_plot("time_series", brush=ui.brush_opts(direction="x")),
        ui.output_ui("annotator"),
        ui.output_table("annotations"),
        ui.output_text_verbatim("path")
    )
)


app_ui = ui.page_fluid(
    ui.panel_title(ui.h2("Py-Shiny static plotting examples", 
                         class_="text-center")),
    ui.br(class_="py-3"),
    ui.div(nav, style="max-width: 90%; margin: auto"),
)


def server(input: Inputs, output: Outputs, session: Session):
    annotation_values = reactive.Value(None)

    @reactive.Effect
    @reactive.event(input.annotate_button)
    def _():
        selected = selected_data().copy()
        selected["annotation_new"] = input.annotation()
        selected = selected.loc[:, ["id", "annotation_new"]]

        df = ts_data().copy()

        df = df.merge(selected, on="id", how="left")
        df["annotation_new"] = df["annotation_new"].fillna("")
        updated_rows = df["annotation_new"] != ""
        df.loc[updated_rows,
               "annotation"] = df.loc[updated_rows,
                                      "annotation_new"]
        df = df.loc[:, ["date_of_week", "classes", "id", "annotation"]]
        annotation_values.set(df)

    @reactive.Calc
    def ts_data():


        dataframe = pd.DataFrame(
            {
                "date_of_week": np.array(
                    [datetime.datetime(2021, 11, i + 1) for i in range(7)]
                ),
                "classes": [5, 6, 8, 2, 3, 7, 4],
                "id": range(7),
                "annotation": [""] * 7
            }
        )

        annotated = annotation_values.get()
        if annotated is None:
            out = dataframe
        else:
            out = annotated
        return out

    @reactive.Calc
    def selected_data():
        out = brushed_points(ts_data(), 
                             input.time_series_brush(), 
                             xvar="date_of_week")
        return out

    @reactive.Calc
    def plot_reactive():
        out = sns.scatterplot(
            data=ts_data(), x="date_of_week", y="classes", hue="annotation"
        )
        out.tick_params(axis="x", rotation=30)
        return out.get_figure()

    @output
    @render.plot
    def time_series():
        return plot_reactive()

    @output
    @render.text
    def path():
        return "\n".join([str(i) for i in os.environ.items()])

    @output
    @render.ui
    def annotator():
        if input.time_series_brush() is not None:
            selected = selected_data().copy()

            min = str(selected["date_of_week"].min())
            max = str(selected["date_of_week"].max())

            min = min.replace(" 00:00:00", "")
            max = max.replace(" 00:00:00", "")

            out = ui.TagList(
                ui.row(
                    ui.column(
                        4,
                        ui.p(f"Dates: {min} to {max}"),
                    ),
                    ui.column(
                        4,
                        ui.input_text("annotation", ""),
                    ),
                    ui.column(4, ui.input_action_button("annotate_button", 
                                                        "Submit")),
                )
            )
            return out

    @output
    @render.table()
    def annotations():
        return ts_data()

    @session.download()
    def download_report():
        file = write_pickle(plot_reactive())
        ext = input.format()
        cmd = f"quarto render report.qmd -o report.{ext} -P plot_path:{file} --to {ext}"
        os.system(cmd)    
        path = f"report.{ext}"
        return path


def write_pickle(obj): 
    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as file:
        # Use pickle to serialize the object to the temporary file
        pickle.dump(obj, file)
        temp_file_path = file.name

    # Return the path to the temporary file
    return temp_file_path


app = App(app_ui, server)
