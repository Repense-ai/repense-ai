from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My App")

@mcp.tool()
def get_diet(bmi: float) -> str:
    """Get the diet plan based on BMI"""
    return "Coma mais vegetais e frutas"

if __name__ == "__main__":
    mcp.run()
