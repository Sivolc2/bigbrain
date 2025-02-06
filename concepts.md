
Brain core:
- Reasoning chain of thought. Endless process that acts through thought, and receives feedback at every step.
	- Brain core awareness only occurs on change. Gathering new info, turn based game, after steps are implemented
- Each loop receives:
	- Response from workflows triggered
	- Metrics from existing senses (Like a video game UI. Health of previous and some meta points, costs, etc)
		- Each 'sense' has a cadence: at baseline applies at each reasoning step
- Able to trigger set of tools
	- Basic tool collection in existing libraries
	- "Sensory organs" API that links to specific queries and actions
		- Metrics on model successes
	- Register a new workflow
		- Set of tools + LLM models called in a graph
	- Apply a workflow 
		- Set parameters (input/output/logging/etc)
Give model a preset workflow to start

Questions:
- Data management, how does it link the workflow to the result? Passing a high level request to the model, which has to connect? Giving the model certain data streams in the declarations that already exist?
	- Starting case: give it a series of existing and validated sensory streams (Eg time series stock market data)
	- Allow the model to expand, or call a workflow that executes creating a new 'sense' (likely point of failure and loops, watch carefully)
- Who decides context for each model? Brain provides initialization and prompt to model, but how does it manage the process?
	- Start by having a central "context" file the brain can update and serve to other models
	- Expand into central RAG, process management.
	- Expand into having a gated process with a "librarian" model that the agent can request information from.

Brain sees purely from a game perspective:
- Video Game UI that gives costs for tasks:
	- Cost to create an "agent" with certain traits
	- Cost to execute actions
	- Traits/components that give usefulness for agents


MVP:
- Model stream of consciousness running
	- Pre-phase:
		- History/Static memory is loaded in
		- Game statistics are provided (Success metrics and others)
	- Action phase:
		- Model is presented with UI: set of actions that can be taken:
			- Model can choose to deploy agents (LLMs with tools) with specific objectives
			- Or Workflows (collections of agents+tools in specific existing pattern)
	- Conclusion phase:
		- Agents/Workflows that were spawned return results
