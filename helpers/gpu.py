"""
Created on 16 lip 2021

@author: spasz
"""

import platform
from subprocess import check_output
from typing import Optional

# Default subprocess calls timeout
defaultTimeout = 10


def IsCuda() -> bool:
    """Checks if GPU cuda is installed and working."""
    try:
        check_output(["nvcc", "--version"], timeout=defaultTimeout)
        return True
    except:
        return False


def CudaDeviceLowestMemory() -> Optional[int]:
    """Returns index of GPU with lowest memory."""
    try:
        return int(
            check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.free,index",
                    "--format=csv,nounits,noheader",
                ],
                timeout=defaultTimeout,
            )
            .decode()
            .split("\n")[-2]
            .split(",")[1]
        )

    # Default to 0 if no GPU found
    except:
        return None


def GetOsDescription() -> str:
    """
    Return full uname description :
    - uname_result(system='Linux', node='spasz-praca',
    release='4.15.0-194-generic', version='#205-Ubuntu SMP Fri Sep 16 19:49:27 UTC 2022',
    machine='x86_64', processor='x86_64')
    """
    return platform.uname()


def GetOsVersion() -> str:
    """
    Returns shorter OS version :
    - Linux-4.15.0-194-generic-x86_64-with-Ubuntu-18.04-bionic
    """
    return platform.platform()


def GetHostname() -> str:
    """Return host name / node name"""
    return platform.node()


def GetHostOsName() -> str:
    """Returns combined names."""
    return GetHostname() + GetOsVersion()
