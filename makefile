ifndef VERBOSE
.SILENT:
endif

# main build target. compiles the teamserver and client
all: ts-build client-build

# teamserver building target
ts-build:
	@ echo "[*] building teamserver"
	# @ ./teamserver/Install.sh
	@ sed -i 's/ctx\.Header("Server", "nginx")/ctx.Header("Server", "nginx\/1.28.0")/' teamserver/pkg/handlers/http.go
	@ sed -i '/ctx\.Header("Content-Type", "text\/html")/d' teamserver/pkg/handlers/http.go
	@ sed -i '/ctx\.Header("X-Havoc", "true")/d' teamserver/pkg/handlers/http.go
	@ find . -type f -exec sed -i 's/0x[dD][eE][aA][dD][bB][eE][eE][fF]/0xaabbccdd/g' {} + 2>/dev/null
	@ cd teamserver; GO111MODULE="on" go build -ldflags="-s -w -X cmd.VersionCommit=$(git rev-parse HEAD)" -o ../havoc main.go
	@ sudo setcap 'cap_net_bind_service=+ep' havoc # this allows you to run the server as a regular user

dev-ts-compile:
	@ echo "[*] compile teamserver"
	@ cd teamserver; GO111MODULE="on" go build -ldflags="-s -w -X cmd.VersionCommit=$(git rev-parse HEAD)" -o ../havoc main.go 

ts-cleanup: 
	@ echo "[*] teamserver cleanup"
	@ rm -rf ./teamserver/bin
	@ rm -rf ./data/loot
	@ rm -rf ./data/x86_64-w64-mingw32-cross 
	@ rm -rf ./data/havoc.db
	@ rm -rf ./data/server.*
	@ rm -rf ./teamserver/.idea
	@ rm -rf ./havoc

# client building and cleanup targets 
client-build: 
	@ echo "[*] building client"
	@ git submodule update --init --recursive
	@ find . -type f -exec sed -i 's/0x[dD][eE][aA][dD][bB][eE][eE][fF]/0xaabbccdd/g' {} + 2>/dev/null
	@ mkdir client/Build; cd client/Build; cmake ..
	@ if [ -d "client/Modules" ]; then echo "Modules installed"; else git clone https://github.com/HavocFramework/Modules client/Modules --single-branch --branch `git rev-parse --abbrev-ref HEAD`; fi
	@ find . -type f -exec sed -i 's/0x[dD][eE][aA][dD][bB][eE][eE][fF]/0xaabbccdd/g' {} + 2>/dev/null
	@ cmake --build client/Build -- -j 4

client-cleanup:
	@ echo "[*] client cleanup"
	@ rm -rf ./client/Build
	@ rm -rf ./client/Bin/*
	@ rm -rf ./client/Data/database.db
	@ rm -rf ./client/.idea
	@ rm -rf ./client/cmake-build-debug
	@ rm -rf ./client/Havoc
	@ rm -rf ./client/Modules


# cleanup target 
clean: ts-cleanup client-cleanup
	@ rm -rf ./data/*.db
	@ rm -rf payloads/Demon/.idea
