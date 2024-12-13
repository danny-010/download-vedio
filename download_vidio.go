package main

import (
	"bufio"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

func getUrls(urlPath string) []string {
	fi, err := os.Open(urlPath)
	if err != nil {
		fmt.Printf("Error: %s\n", err)
		panic(err)
	}
	defer fi.Close()
	var urls []string

	br := bufio.NewReader(fi)
	for {
		url, _, c := br.ReadLine()
		if c == io.EOF {
			break
		}
		urls = append(urls, (string(url)))
	}
	return urls
}

var urlPtah string
var distDir string

func init() {

	// 2. 注册需要解析的命令行参: 参数名、默认值、参数说明
	flag.StringVar(&urlPtah, "urlPtah", "./", "url的路径")
	flag.StringVar(&distDir, "distDir", "./", "素材存储路径")

	// 3. 解析命令行参数
	flag.Parse()
}

func main() {
	fmt.Println(urlPtah, distDir)
	flag.Parse()

	for _, url := range getUrls(urlPtah) {
		if len(url) < len("http://") {
			continue
		}
		filename := strings.Split(url, "/")
		err := DownloadFile(distDir+"/"+filename[len(filename)-1]+".mp4", strings.TrimSpace(url))
		if err != nil {
			fmt.Println("download REEOR: ", err, url)
			continue
		}
		fmt.Println("Downloaded ok: " + url)
	}
}

// DownloadFile will download a url to a local file. It's efficient because it will
// write as it downloads and not load the whole file into memory.
func DownloadFile(filepath string, url string) error {

	// Get the data
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// Create the file
	out, err := os.Create(filepath)
	if err != nil {
		return err
	}
	defer out.Close()
	fmt.Println(resp.ContentLength)

	// Write the body to file
	_, err = io.Copy(out, resp.Body)
	return err
}
