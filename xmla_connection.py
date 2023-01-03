import CLR
from CLR.System.Reflection import Assembly

Assembly.LoadWithPartialName("AnalysisServices.DLL")

from CLR.Microsoft.AnalysisServices import Server
from CLR.Microsoft.AnalysisServices import ProcessType
