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

local charset = { 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's',
                  'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm', 'Q',
                  'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'A', 'S', 'D', 'F', 'G', 'H',
                  'J', 'K', 'L', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '1', '2', '3', '4', '5',
                  '6', '7', '8', '9', '0' }

function string.random(length)
    if length > 0 then
        return string.random(length - 1) .. charset[math.random(1, #charset)]
    else
        return ""
    end
end

local function uuid()
    return UUID():gsub('-', '')
end

request = function()
    local value = math.random(1000)
    -- local user_index = math.random(0, 99)
    -- local username = "username_" .. tostring(user_index)
    -- local password = "password_" .. tostring(user_index)
    -- local title = movie_titles[movie_index]
    -- local rating = math.random(0, 10)
    -- local text = string.random(256)

    local method = "POST"
    local headers = {}
    local param = {
        args = {
            -- username, password, title, rating, text
            value
        },
        req_id = uuid()
    }
    local body = JSON:encode(param)
    headers["Content-Type"] = "application/json"
    headers["Host"] = "caller1.default.example.com"

    return wrk.format(method, path, headers, body)
end