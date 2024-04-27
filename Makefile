APP=$(shell basename $(shell git remote get-url origin))
# REGISTRY=gcr.io/$(shell echo ${PROJECT_ID})
REGISTRY=$(shell echo ${DOCKERHUB_USERNAME})

VERSION=$(shell git describe --tags --abbrev=0)
SHA=$(shell git rev-parse --short HEAD)

# Target OS (Uncomment one of the next!)
TARGET_OS=linux
# TARGET_OS=windows
# TARGET_OS=darwin

# Target architecture (Uncomment one of the next!)
TARGET_ARCH=amd64
# TARGET_ARCH=arm64


format:	
	gofmt -s -w ./

lint:
	golint

test:
	go test -v

get:
	go get

build: format get
	CGO_ENABLED=0 GOOS=${TARGET_OS} GOARCH=${TARGET_ARCH} go build -v -o kbot -ldflags "-X="github.com/vlad-batrak/telegram-bot/cmd.appVersion=${VERSION}

image:
	docker build . -t ${REGISTRY}/${APP}:${VERSION}-${SHA}-${TARGET_ARCH}

push:
	docker push ${REGISTRY}/${APP}:${VERSION}-${SHA}-${TARGET_ARCH}

clean:
	rm -rf kbot
	docker rmi -f ${REGISTRY}/${APP}:${VERSION}-${SHA}-${TARGET_ARCH}


helm:
	helm create helm

helm-lint:
	helm lint ./helm

helm-template: helm-lint
	helm template kbot ./helm

helm-pack:
	helm package ./helm -u -d ./releases --app-version "${VERSION}-${SHA}"

helm-rollback:
	$(shell read -p "Enter REVISION " REVISION)
	helm rollback kbot ${REVISION}

helm-clean:
	helm uninstall kbot