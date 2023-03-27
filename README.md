# The General Ideas
An agent based model which looks to explain the alcohol harm paradox through fundamental cause theory (FCT). 

## Alcohol Harm Paradox
The alcohol harm paradox is a phenomenon in which two people who drink the same amount of alcohol over thier lifetimes will experience different alcohol harms based on their socioeconomic background. Individuals lower on the socioeconomic scale experience more alcohol harms when compared to those high on the socioeconomic scale, even when drinking less on average. 


## Fundamental Cause Theory
Is a social theory that proposes that the fundamental causes of disease can be linked to socioeconomic status. It proposes that the level of education, personal wealth, social connections and social influence are liked to the likelihood of an individual to get succumb to disease.

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

