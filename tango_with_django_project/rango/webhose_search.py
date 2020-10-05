import json
import urllib.parse
import urllib.request


def read_webhose_key():
    """
    从 search.key 文件中读取 Webhose API 密钥
    返回 None（未找到密钥），或者密钥的字符串形式
    注意：把 search.key 写入 .gitignore 文件，禁止提交
    """
    webhose_api_key = None
    try:
        with open('search.key', 'r') as f:
            webhose_api_key = f.readline().strip()
    except:
        raise IOError('search.key file not found')
    return webhose_api_key


def run_query(search_terms, size=10):
    """
    指定搜索词条和结果数量（默认为 10），把 Webhose API 返回的结果存入列表
    每个结果都有标题、链接地址和摘要
    """
    webhose_api_key = read_webhose_key()
    if not webhose_api_key:
        raise KeyError('Webhose key not found')
    root_url = 'http://webhose.io/search'
    # 处理查询字符串，转义特殊字符
    query_string = urllib.parse.quote(search_terms)
    # 使用字符串格式化句法构建完整的 API URL
    search_url = ('{root_url}?token={key}&format=json&q={query}'
                  '&sort=relevancy&size={size}').format(root_url=root_url,
                                                        key=webhose_api_key,
                                                        query=query_string,
                                                        size=size)
    results = []
    try:
        # 连接 Webhose API，把响应转换为 Python 字典
        response = urllib.request.urlopen(search_url).read().decode('utf-8')
        json_response = json.loads(response)
        # 迭代文章，把一篇文章作为一个字典追加到结果列表中,限制摘要的长度为 200 个字符
        for post in json_response['posts']:
            results.append({'title':post['title'],
                            'link': post['url'],
                            'summary': post['text'][:200]})
    except:
        print("Error when querying the webhose API")
    # 把结果列表返回给调用方
    return results
