import json

cookies = 'bid=NulHfSznh4Q; douban-fav-remind=1; _vwo_uuid_v2=DC7E299AC0DCAD57725551FB3E9BC52E6|79770cc69479b99098ad9e06c26a2748; push_doumail_num=0; gr_user_id=8ba9f9a6-9872-4f54-9e64-59e2e2ca590f; douban-profile-remind=1; viewed="30175598"; ct=y; ll="108296"; dbcl2="51476394:++j1PWRmpmU"; push_noty_num=0; ck=sD9U; ap_v=0,6.0; frodotk="ce7ea0fb3059b1a16b7be2f1910d14e3"'

def parse_cookies(cookie_str):
    # 格式化cookies为字典列表
    cookie_list = cookie_str.split('; ')
    cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookie_list}
    return cookies


if __name__ == '__main__':
    cookies_for_request = parse_cookies(cookies)
    with open("request_cookies.txt", 'w') as fw:
        fw.write(json.dumps(cookies_for_request))