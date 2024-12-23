import asyncio
import websockets
import json

async def client_example():
    uri = "ws://localhost:8000/process"
    async with websockets.connect(uri) as websocket:
        # Send initial tweet
        await websocket.send(json.dumps({
            "tweet": "Exciting new AI breakthrough just announced! #AIRevolution"
        }))
        
        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                
                print("Received:", data)
                
                # Handle different interaction points
                if data['status'] == 'awaiting_style_selection':
                    await websocket.send(json.dumps({
                        "selected_style": "Professional Technical"
                    }))
                
                if data['status'] == 'awaiting_review':
                    await websocket.send(json.dumps({
                        "feedback": "approve"
                    }))
                
                if data['status'] == 'published':
                    break
                
            except Exception as e:
                print(f"Error: {e}")
                break


# Create an event loop
loop = asyncio.get_event_loop()

# Run the async function
loop.run_until_complete(client_example())

# Close the event loop
loop.close()