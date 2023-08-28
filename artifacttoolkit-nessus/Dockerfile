#Use the latest Nessus image as a base
FROM tenableofficial/nessus:latest

# Update the system
#RUN apt update && apt upgrade -y

EXPOSE 8443 8834

ENTRYPOINT [ "/opt/nessus/sbin/nessusd" ]
CMD ["start"]
