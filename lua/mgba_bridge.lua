local host = "127.0.0.1"
local port = 54321

local server, bind_error = socket.bind(host, port)
if not server then
    console:error("Could not bind bridge socket: " .. tostring(bind_error))
    return
end

local listen_result, listen_error = server:listen(1)
if not listen_result then
    console:error("Could not listen on bridge socket: " .. tostring(listen_error))
    return
end

local client = nil
console:log(string.format("PokeMonitor bridge listening on %s:%d", host, port))

local function close_client()
    if client then
        client:close()
        client = nil
    end
end

local function reply(message)
    if client then
        client:send(message .. "\n")
    end
end

local function bytes_to_hex(data)
    local hex = {}
    for i = 1, #data do
        hex[#hex + 1] = string.format("%02x", data:byte(i))
    end
    return table.concat(hex)
end

local function handle_command(command)
    local op, address_text, length_text = command:match("^(%S+)%s+(%S+)%s*(%S*)")

    if op ~= "read32" and op ~= "readbytes" then
        reply("ERR expected: read32 <address> or readbytes <address> <length>")
        return
    end

    local address = tonumber(address_text)
    if not address then
        reply("ERR invalid address")
        return
    end

    if not emu then
        reply("ERR no game is loaded")
        return
    end

    if op == "read32" then
        reply(string.format("0x%08x", emu:read32(address)))
        return
    end

    local length = tonumber(length_text)
    if not length then
        reply("ERR invalid length")
        return
    end

    reply(bytes_to_hex(emu:readRange(address, length)))
end

callbacks:add("frame", function()
    if not client then
        if server:hasdata() then
            local accepted = server:accept()
            if accepted then
                client = accepted
            end
        end
        return
    end

    if client:hasdata() then
        local command, receive_error = client:receive(128)
        if command then
            handle_command(command)
            close_client()
        else
            console:warn("Bridge receive failed: " .. tostring(receive_error))
            close_client()
        end
    end
end)
