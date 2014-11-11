#!/usr/bin/wolfram -script
f[x_]:=x-AbsoluteTime[{1970,1,1,0,0,0}];
year = ToExpression[$CommandLine[[4]]]
month = ToExpression[$CommandLine[[5]]]
day = ToExpression[$CommandLine[[6]]]
  raw = WeatherData["LFBO", "Temperature", {year, month, day}]; //AbsoluteTiming
times = Map[f, raw["Times"]]; //AbsoluteTiming
values = raw["Values"];
out = Table[
	    StringJoin[ToString[times[[i]]], ":", ToString[values[[i]]]], {i, 1, Length[times]}
	    ];//AbsoluteTiming
Print[out]

