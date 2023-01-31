# FCT_Python
An agent based model which looks to explain the alcohol harm paradox through the lens of fundamental cause theory. 

## Alcohol Harm Paradox

## Fundamental Cause Theory

## Mechanism-based Social Systems Modelling

``` mermaid

flowchart 


subgraph MBSSM
direction TB

%% MACRO LEVEL
	subgraph macro ["Macro Level"]
	direction TB

		subgraph Entities ["Macro Entities"]

			SE("Social Entities")
			SP("Social Phenomena")
			SE--"Macro Interaction"-->SP--"Macro Interaction"-->SE
		end

end


%% MICRO LEVEL
	subgraph micro ["Micro Level"]
	direction TB
	%%A B

		subgraph agents ["Micro Entities"]
			direction LR
			a1(((a1)))
			a2(((a2)))
			a3(((a3)))
		end
end


macro -- "Situational Mechanisms"--> micro -- "Transformational Mechanisms" --> macro


end




a1 & a2 -- "micro interaction"--- a3
a1 & a3 -- "micro interaction"--- a2
a2 & a3 -- "micro interaction"--- a1


```

