#!/bin/bash

echo "Automatic benchmark bash script"
# check if correct number of arguments provided
if [ $# -ne 4 ]; then
  echo "Error: 4 arguments required (ssh pkey, server and client public IPs and then the private server IP)"
  exit 1
fi

# store IPs in variables
sshkey=$1
server_ip=$2
client_ip=$3
private_server_ip=$4

# Setup server if needed
if ! sudo ssh -q -i "$sshkey" ec2-user@"$server_ip" "command -v cargo" &> /dev/null
then
    echo "Installing the required programs on the server..."
    sudo ssh -q -i "$sshkey" ec2-user@"$server_ip" <<EOF
    wget https://github.com/Carbonhell/RustWebserversBenchmark/archive/refs/heads/master.zip;
    unzip master.zip
    rm master.zip
    curl https://sh.rustup.rs -sSf > RUSTUP.sh
    sh RUSTUP.sh -y
    source "$HOME/.cargo/env"
    sudo yum install gcc -y
EOF
fi

# Setup client if needed
if ! sudo ssh -q -i "$sshkey" ec2-user@"$client_ip" "command -v ab" &> /dev/null
then
    echo "Installing the required programs on the server..."
    sudo ssh -q -i "$sshkey" ec2-user@"$client_ip" <<EOF
    sudo yum install httpd-tools -y
EOF
fi


webservers=("actix-web-bench" "rocket-bench" "axum-bench")
test_folders=("Single" "Small" "Medium" "Large")
server_type=("Normal" "Compression" "SingleThreaded")
concurrency_levels=("1" "25" "50" "75" "100" "150" "200")
requests="20000"

for webserver in "${webservers[@]}"; do
  if [[ "${webserver}" != "actix-web-bench" ]]; then
    commands=("cargo run --release" "cargo run --release --features compression -- -c" "cargo run --release -- -s")
  elif [[ "${webserver}" != "rocket-bench" ]]; then
    commands=("ROCKET_PORT=8080 cargo run --release" "ROCKET_PORT=8080 cargo run --release --features=compression" "ROCKET_PORT=8080 ROCKET_WORKERS=1 cargo run --release")
  elif [[ "${webserver}" != "axum-bench" ]]; then
    commands=("cargo run --release" "cargo run --release --features=compression" "cargo run --release --features=single_threaded")
  fi

  # For each web server type (Normal, Compression enabled, Forced single thread)
  for command_key in "${!commands[@]}"; do
    # Run a test for each static workload configuration: Single, Small, Medium, Large
    for test_type_key in "${!test_folders[@]}"; do
      echo "Test type is ${test_folders[${test_type_key}]}."
      # If not single, set the image to the correct size
      if [ "${test_folders[${test_type_key}]}" != "Single" ]; then
        echo "Setting static workload image size..."
        sudo ssh -i "$sshkey" ec2-user@"$server_ip" <<EOF
        cd ~/RustWebserversBenchmark-master
        python3 set_workload_size.py ${test_type_key}
EOF
        echo "Set."
      fi

      for concurrency_level in "${concurrency_levels[@]}"; do
        # Restart the server for each group of repetitions
        echo "Starting ${webserver}..."
        sudo ssh -i "$sshkey" ec2-user@"$server_ip" <<EOF
          pkill actix-web-bench
          pkill rocket-bench
          pkill axum-bench
          pkill cargo
          unset ROCKET_WORKERS
          cd ~/RustWebserversBenchmark-master/${webserver}
          nohup ${commands[${command_key}]} >/dev/null 2>&1 &
EOF
        printf "Waiting for the server to be ready..."
        while ! sudo ssh -q -i "$sshkey" ec2-user@"$client_ip" "curl --output /dev/null --silent --head --fail http://${private_server_ip}:8080/single_page.html" ; do
            printf "."
            sleep 5
        done

        echo "Web server ready."

        # Repeat each test thrice
        for i in "1" "2" "3"; do
          if [[ "${test_folders[${test_type_key}]}" != "Single" ]]; then
            target_page="index.html";
          else
            target_page="single_page.html";
          fi
          benchmark_cmd="ab -n ${requests} -c ${concurrency_level} -k http://${private_server_ip}:8080/${target_page} >${i}.txt 2>&1"
          echo "Benchmark command is: ${benchmark_cmd}"
          sudo ssh -i "$sshkey" ec2-user@"$client_ip" "${benchmark_cmd}"

          result_dir=./Results/${webserver}/${server_type[${command_key}]}/"${test_folders[${test_type_key}]}/${concurrency_level}"
          mkdir -p "${result_dir}"
          sudo scp -q -i "$sshkey" ec2-user@"$client_ip":~/${i}.txt "${result_dir}"/"${i}".txt
        done

      done
    done
  done

done
