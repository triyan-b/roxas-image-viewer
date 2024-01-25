# roxas-image-viewer

### Install and run

For now, the app is not bundled as an executable so you will have to install Python.

Dependencies: Windows, Python 3, tkinter, pandas, pyyaml

1. [Download and install](https://www.anaconda.com/download) the latest Anaconda (provides Python + conda package manager) with default settings

2. Install app dependencies  
    a. Open a command prompt/Powershell window and check conda by running the following line. You may need to add `C:\path\to\anaconda3`, `C:\path\to\anaconda3\Scripts` and `C:\path\to\anaconda3\Library\bin` to your Path system variable (replace `C:\path\to\anaconda3` with your Anaconda install location)
    ```
    conda --version
    ```
    b. Now check whether you can run python.   
    ```
    python --version
    ```
    c. Install dependencies:
    ```
    conda install pandas pyyaml
    ```


2. Clone or download and unzip this repository

```
git clone git@github.com:triyan-b/roxas-image-viewer.git
```

3. Double click `Roxas Image Viewer.bat` to run the app

4. [Optional]: Create a shortcut to `Roxas Image Viewer.bat` and place it where you please. You can also set its icon ([.ico file](icon.ico) is provided)

### Configuration

You can change the default settings in [settings.yaml](settings.yaml)

### Keyboard shortcuts

`Enter`: Go to next stage (e.g. Setup -> Sample Viewer -> Subsample Viewer -> Subsample Evaluation)  
`ALT`+`Left Arrow`: Go back  
`ALT`+`I`: Open the currently selected image in the default image viewer  
`ALT` + `V`: View all evaluations (only on Sample Viewer page)  
`ALT` + `E`: Export all evaluations (only on Sample Viewer page)  

### Troubleshoooting

In case of unexpected behaviour:

- Ensure the path to pythonw.exe (e.g. C:\ProgramData\anaconda3) is added to the Path system variable or edit `Roxas Image Viewer.bat` to use the full path to the .exe
- Ensure `pandas` and `yaml` are installed:
```
conda install pandas pyyaml
```
- Contact the developer
