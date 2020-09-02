# 西安交大图书馆自动预约
## 部署 | Deploy
### 环境要求 | Environment
* python >= 3.5
* python-pip
* python-virtualenv
* 进程监视(e.g. supervisor)
### 流程 | Process
* 配置虚拟环境，运行 `virtualenv ./venv`  
* 启动虚拟环境，运行 `source ./venv/bin/activate`  
* 安装依赖，运行 `pip3 install -r requirements.txt`  
* 配置运行信息，运行 `python3 setup.py`
* 退出虚拟环境，运行 `deactivate`
* 配置进程监视
## 开发者 | Contributors
* 代码： [f(x, z)=xzx](https://github.com/XuZhixuan)
## LICENSE
[MIT License](https://opensource.org/licenses/MIT)  

    Copyright (c) 2020 f(x,z)=xzx

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
