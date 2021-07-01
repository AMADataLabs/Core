# How to build
Under Source/Talend there is a folder called "pdr_job".
This directory needs to be imported into a Talend workspace. see [this guide](https://help.talend.com/r/VXLHZvns6nwhPGeQbm1Iig/hJXF3051B1q_2bHR6EUUHw).
Then a standalone job needs to be built from the imported item. see [this guide](https://help.talend.com/r/VXLHZvns6nwhPGeQbm1Iig/8_bKO5gGEa4p2yCW5KHdDA)
The standalone job must be build as a .zip file not a directory.
The standalone .zip file will look like `pdr_job_X.Y.zip` which `X` and `Y` make the version built.
The standalone .zip file needs to be put in the same directory as the Dockerfile.