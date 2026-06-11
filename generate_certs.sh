#!/bin/bash
# Generates self-signed certificates for Modbus TLS

mkdir -p certs
cd certs

echo "Generating private key..."
openssl genrsa -out server.key 2048

echo "Generating self-signed certificate..."
openssl req -new -x509 -key server.key -out server.crt -days 365 -subj "/C=ES/ST=Madrid/L=Madrid/O=Snocomm/OU=Industrial/CN=ahf.snocomm.local"

echo "Certificates generated in /certs directory:"
ls -l
