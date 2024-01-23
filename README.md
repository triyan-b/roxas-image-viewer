# roxas-image-viewer

### Install and run

Dependencies: Windows, Python 3, pandas, pyyaml

1. Clone or download and unzip this repository

```
git clone git@github.com:triyan-b/roxas-image-viewer.git
```

2. Double click `Roxas Image Viewer.bat` to run the app

3. [Optional]: Create a shortcut to `Roxas Image Viewer.bat` and place it where you please. You can also set its icon ([.ico file](icon.ico) is provided)

### Configuration

You can change the default settings in [settings.yaml](settings.yaml)

### Troubleshoooting

In case of unexpected behaviour:

- Ensure the path to pythonw.exe (e.g. C:\ProgramData\anaconda3) is added to the Path system variable or edit `Roxas Image Viewer.bat` to use the full path to the .exe
- Ensure `pandas` and `yaml` are installed:
```
conda install pandas pyyaml
```
- Contact the developer
