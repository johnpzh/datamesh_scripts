
if __name__ == "__main__":
    siftfile = 'SIFT.chr1.vcf'
    
    # Write
    with open(siftfile, 'w') as f:
        f.write("Line 1\nLine 2\n")

    # Read
    with open(siftfile, 'r') as f:
        content = f.readlines()
        print(f"len(content): {len(content)}")
