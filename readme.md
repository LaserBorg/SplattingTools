# synthetic Splatting & NeRF Data from 3DS Max


## install pip packages in 3ds Max 2025 python
execute Commandline (cmd) with admin privileges:
```bash
cd C:\Program Files\Autodesk\3ds Max 2025\Python  
python -m ensurepip --upgrade --user  
python -m pip install --upgrade pip  
python -m pip install --user open3d numpy
```


## export PLY with 32bit float dtpye 
using tensor API in Open3d:  
https://github.com/isl-org/Open3D/issues/1325

## WebViewer
Viewer using PlayCanvas Orbit camera:  
https://konzept.staging.visionsbox.de/dt/splat/orbit/

Viewer using modified SuperSplat export:  
https://konzept.staging.visionsbox.de/dt/splat/



## links to manuals
- [pymxs](https://help.autodesk.com/view/MAXDEV/2025/ENU/?guid=MAXDEV_Python_using_pymxs_html)
- [PostShot](https://www.jawset.com/docs/d/Postshot+User+Guide/Importing+Images)
