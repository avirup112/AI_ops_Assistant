"""LangGraph orchestration for the AI Operations Assistant."""
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent

class AssistantState(TypedDict):
    """State structure for the AI Operations Assistant."""
    user_task: str
    execution_plan: Dict[str, Any]
    execution_results: Dict[str, Any]
    final_response: Dict[str, Any]
    error: str
    current_step: str

class AIOperationsGraph:
    """LangGraph orchestration for the multi-agent AI Operations Assistant."""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.verifier = VerifierAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""
        # Create the state graph
        workflow = StateGraph(AssistantState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("executor", self._executor_node)
        workflow.add_node("verifier", self._verifier_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # Set entry point
        workflow.set_entry_point("planner")
        
        # Add edges with conditional routing
        workflow.add_conditional_edges(
            "planner",
            self._should_continue_after_planning,
            {
                "continue": "executor",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "executor",
            self._should_continue_after_execution,
            {
                "continue": "verifier",
                "error": "error_handler"
            }
        )
        
        workflow.add_edge("verifier", END)
        workflow.add_edge("error_handler", END)
        
        return workflow.compile()
    
    def _planner_node(self, state: AssistantState) -> AssistantState:
        """Execute the planner agent."""
        print("🧠 Planning phase: Converting task to execution plan...")
        
        try:
            user_task = state["user_task"]
            plan_result = self.planner.create_plan(user_task)
            
            if plan_result["success"]:
                state["execution_plan"] = plan_result["plan"]
                state["current_step"] = "planning_complete"
                print(f"✅ Plan created with {len(plan_result['plan']['steps'])} steps")
            else:
                state["error"] = f"Planning failed: {plan_result.get('error', 'Unknown error')}"
                state["current_step"] = "planning_failed"
                print(f"❌ Planning failed: {state['error']}")
            
        except Exception as e:
            state["error"] = f"Planner node error: {str(e)}"
            state["current_step"] = "planning_failed"
            print(f"❌ Planner error: {state['error']}")
        
        return state
    
    def _executor_node(self, state: AssistantState) -> AssistantState:
        """Execute the executor agent."""
        print("⚡ Execution phase: Running planned steps...")
        
        try:
            execution_plan = state["execution_plan"]
            execution_result = self.executor.execute_plan(execution_plan)
            
            state["execution_results"] = execution_result
            
            if execution_result["success"]:
                state["current_step"] = "execution_complete"
                stats = execution_result.get("stats", {})
                print(f"✅ Execution completed: {stats.get('successful_steps', 0)}/{stats.get('total_steps', 0)} steps successful")
            else:
                state["current_step"] = "execution_partial"
                print(f"⚠️ Execution completed with issues: {execution_result.get('message', 'Unknown issue')}")
            
        except Exception as e:
            state["error"] = f"Executor node error: {str(e)}"
            state["current_step"] = "execution_failed"
            print(f"❌ Executor error: {state['error']}")
        
        return state
    
    def _verifier_node(self, state: AssistantState) -> AssistantState:
        """Execute the verifier agent."""
        print("🔍 Verification phase: Validating and formatting results...")
        
        try:
            execution_results = state["execution_results"]
            user_task = state["user_task"]
            
            verification_result = self.verifier.verify_and_format(execution_results, user_task)
            
            state["final_response"] = verification_result
            
            if verification_result["success"]:
                state["current_step"] = "verification_complete"
                print("✅ Verification and formatting completed")
            else:
                state["error"] = f"Verification failed: {verification_result.get('error', 'Unknown error')}"
                state["current_step"] = "verification_failed"
                print(f"❌ Verification failed: {state['error']}")
            
        except Exception as e:
            state["error"] = f"Verifier node error: {str(e)}"
            state["current_step"] = "verification_failed"
            print(f"❌ Verifier error: {state['error']}")
        
        return state
    
    def _error_handler_node(self, state: AssistantState) -> AssistantState:
        """Handle errors and create error response."""
        print("🚨 Error handling phase...")
        
        error_message = state.get("error", "Unknown error occurred")
        current_step = state.get("current_step", "unknown")
        
        # Create error response
        error_response = {
            "success": False,
            "error": error_message,
            "step": current_step,
            "message": f"The AI Operations Assistant encountered an error during {current_step}: {error_message}",
            "formatted_response": f"I apologize, but I encountered an error while processing your request.\n\nError: {error_message}\n\nPlease check your configuration and try again."
        }
        
        state["final_response"] = error_response
        state["current_step"] = "error_handled"
        
        print(f"❌ Error handled: {error_message}")
        
        return state
    
    def _should_continue_after_planning(self, state: AssistantState) -> str:
        """Determine whether to continue after planning."""
        if state.get("error"):
            return "error"
        return "continue"
    
    def _should_continue_after_execution(self, state: AssistantState) -> str:
        """Determine whether to continue after execution."""
        if state.get("error"):
            return "error"
        return "continue"
    
    def run(self, user_task: str) -> Dict[str, Any]:
        """
        Run the complete AI Operations Assistant workflow.
        
        Args:
            user_task: Natural language task from the user
            
        Returns:
            Dictionary with the final response
        """
        print(f"🚀 Starting AI Operations Assistant for task: '{user_task}'")
        print("=" * 60)
        
        # Initialize state
        initial_state = AssistantState(
            user_task=user_task,
            execution_plan={},
            execution_results={},
            final_response={},
            error="",
            current_step="initialized"
        )
        
        try:
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            print("=" * 60)
            print("🎉 AI Operations Assistant completed!")
            
            return final_state["final_response"]
            
        except Exception as e:
            print(f"❌ Graph execution failed: {str(e)}")
            return {
                "success": False,
                "error": f"Graph execution failed: {str(e)}",
                "message": "The AI Operations Assistant encountered a critical error",
                "formatted_response": f"I apologize, but I encountered a critical error while processing your request: {str(e)}"
            }