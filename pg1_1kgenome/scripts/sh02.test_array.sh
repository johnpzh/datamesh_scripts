array=(1 2 3)
echo "array: ${array}"
echo "array[0]: ${array[0]}"
echo "array[@]: ${array[@]}"
path=$(readlink -f .)
echo "path: ${path}"
echo "pwd: $(readlink -f .)"