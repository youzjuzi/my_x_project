package com.diy.sys.controller;


import com.diy.config.CaptureConfig;
import com.wf.captcha.SpecCaptcha;
import com.wf.captcha.base.Captcha;
import com.wf.captcha.utils.CaptchaUtil;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

/*
* 验证码
*
* */
@CrossOrigin
@RestController
@RequestMapping
public class CaptureController {
    @RequestMapping("/captcha")
    public void captcha(@RequestParam String key, HttpServletRequest request, HttpServletResponse response) throws Exception{
        //指定验证码长宽与字符数量
        SpecCaptcha specCaptcha = new SpecCaptcha(130, 48, 4);
        //设置类型
        specCaptcha.setCharType(Captcha.TYPE_NUM_AND_UPPER);
        //存储验证码
        CaptureConfig.CAPTURE_MAP.put(key, specCaptcha.text().toLowerCase());
        //System.out.println("key" + key);
        //输出图片
        response.setContentType("image/png");
        specCaptcha.out(response.getOutputStream());
    }
}
