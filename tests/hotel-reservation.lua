local socket = require("socket")
local JSON = require("JSON")
local UUID = require("uuid")
time = socket.gettime() * 1000
UUID.randomseed(time)
math.randomseed(time)
math.random();
math.random();
math.random()

local frontendPath = os.getenv("LOAD_BALANCER_IP")

local function uuid()
    return UUID():gsub('-', '')
end

request = function()
    local user_id = math.random(0, 99)
    local hotel_id = math.random(0, 99)
    local flight_id = math.random(0, 99)

    local method = "POST"
    local headers = {}
    local param = {
        args = {
            tostring(user_id), tostring(flight_id), tostring(hotel_id)
        },
        req_id = uuid()
    }
    local body = JSON:encode(param)
    headers["Content-Type"] = "application/json"
    headers["Host"] = "frontend.default.example.com"

    return wrk.format(method, path, headers, body)
end
