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

### Situational Mechanisms

How agents receive and process information sent from a macro-level entity
``` mermaid 
sequenceDiagram

participant c as Communicator
participant a as Agent
participant m as Mediator 
participant f as FCT


loop Every Tick (week)
c->>a: Communicator sends event to Agent
Note right of a: Agent stores event in list.
Note right of a: Agent chooses an event to attempt to decode.

a->>+m: Agent sends chosen event to Mediator
m->>+f: Mediator sends chosen event to FCT
Note left of f: Decode attempt, success based on FCT parameters. <br> Assuming successful decode:
Note left of f: FCT params altered 
f->>-m: Success/Failure returned with event
m->>-a: Agent stores event in successfully decoded events list
end
```

### Action Mechanisms
Agents are then able to send a decoded event to another agent within their network. 

```  mermaid
sequenceDiagram

actor a1 as Agent 1
actor a2 as Agent 2
participant m as Agent 2 Mediator
participant f as Agent 2 FCT

loop Every Tick (week)

a1-->a1: Find random agent in network
a1->>+a2: Communicate solved event
a2-->a2: Check event isn't solved
Note left of a2: if solved do nothing
a2->>+m: Send event to Mediator
m->>+f: Make FCT alterations
f->>-m: Success returned
m->>-a2: Event stored in successful events
end

```



### Transformational Mechanisms

``` mermaid
stateDiagram-v2
[*] --> update_deprivation_quintile
state update_deprivation_quintile {
    [*] --> loop_agents
    loop_agents --> check_swap_eligibility

check_swap_eligibility --> agent_swap_up: agent is tagged as swapping up
check_swap_eligibility -->agent_doesn't_swap: agent can't swap
check_swap_eligibility --> agent_swap_down: agent is tagged as swapping down
agent_swap_up --> agent_swap_up_list: agent added to swap up list
agent_swap_down --> agent_swap_down_list: agent added to swap down list

agent_swap_up_list-->swap_pair_list
agent_swap_down_list-->swap_pair_list


state swap_pair_list {
    [*] --> for_each_pair
    for_each_pair --> agent_1_dq: get agent 1 deprivation quintile

    for_each_pair --> agent_2_dq: get agent 2 deprivation quintile

		agent_2_dq -->agent_1: agent 1 deprivation quintile set as agent 2 deprivation quintile
		agent_1_dq -->agent_2: agent 2 deprivation quintile set as agent 1 deprivation quintile
		agent_1-->[*]
		agent_2-->[*]
}
swap_pair_list -->[*]

}
```