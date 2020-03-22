# Create local bin folder and add it to PATH
BIN=$HOME/bin
mkdir -p $BIN
export PATH=$PATH:$BIN
echo "Add $HOME/bin to your rc file for future use of kubectl, helm and minikube"

# Install Kubectl, Minikube
curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.17.0/bin/linux/amd64/kubectl
chmod +x kubectl
mv kubectl $BIN
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube
install minikube $BIN

#install jq
wget https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64
chmod +x jq-linux64
mv jq-linux64 $BIN/jq

echo "Starting new VM with 4 CPU and 8GB Memory"
read -p "You can change settings here or continue with default. Do you wish to change?[y/n]" change
if [ $change == 'y' ]; then
  read -p "Memory: " mem
  read -p "vCPU: " cpu
  read -p "VM name: " name
else
  mem=8192
  cpu=4
  name="minikube"
fi
echo "Starting $name VM with $cpu CPUs and $mem Memory"
minikube --memory $mem --cpus $cpu start -p $name --vm-driver=virtualbox
echo "Check minikube running status"
minikube status -p $name
echo "Check kubectl install is proper"
kubectl version

IP=$(minikube ip -p $name)
