
# Results

When returning JSON, here's an example of results: 
```
{
    "date_of_analysis": "2026-06-24T14:59:41.002857",
    "warnings": [],
    "x_metrics": {
        "Field Size Calculation by FWHM (mm)": 200.25600000000003,
        "CAX Offset from Beam Center (mm)": 0.0,
        "Flatness Calculation by Variance (%)": 1.449342757936508,
        "Flatness Calculation by Ratio (IEC) (%)": 102.94131525551693,
        "Flatness Calculation by CAX Variance": 0.4805039558330843,
        "Flatness Calculation by CAX Ratio": 1.030199600484452,
        "Symmetry Calculation by CAX Point Difference (%)": 0.0,
        "Symmetry Calculation by Point Ratio (IEC 976) (%)": 100.0,
        "Symmetry Calculation by Area (%)": 0.0,
        "Field Width (mm)": 200.2570712821681
    },
    "y_metrics": {
        "Field Size Calculation by FWHM (mm)": 200.25600000000003,
        "CAX Offset from Beam Center (mm)": 0.0,
        "Flatness Calculation by Variance (%)": 1.449342757936508,
        "Flatness Calculation by Ratio (IEC) (%)": 102.94131525551693,
        "Flatness Calculation by CAX Variance": 0.4805039558330843,
        "Flatness Calculation by CAX Ratio": 1.030199600484452,
        "Symmetry Calculation by CAX Point Difference (%)": 0.0,
        "Symmetry Calculation by Point Ratio (IEC 976) (%)": 100.0,
        "Symmetry Calculation by Area (%)": 0.0,
        "Field Width (mm)": 200.2570712821681
    }
}
```

`date_of_analysis` is the date time of analysis. 

`warnings` is a list of errors encountered while running the metrics. Note that this does not include errors propogating from outside the metrics analysis. 

`x_metrics` and `y_metrics` have the same keys and give the metrics for the x profile and y profile respectively. 

