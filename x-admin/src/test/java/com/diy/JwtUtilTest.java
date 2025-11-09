package com.diy;

import com.diy.common.utils.JwtUtil;
import com.diy.sys.entity.User;
import io.jsonwebtoken.Claims;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
public class JwtUtilTest {
    @Autowired
    private JwtUtil jwtUtil;


    @Test
    public void JwtUtilTest(){
        User user = new User();
        user.setUsername("xiaoming");
        user.setPhone("123456789");
        String token = jwtUtil.createToken(user);
        System.out.println(token);
    }

    @Test
    public void testParseJwt(){
        String token = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJmNWY4Nzc4Yy02NWRjLTQyYWEtOWM4Yi02MTEyOGQ1ZmQwZTMiLCJzdWIiOiJ7XCJwaG9uZVwiOlwiMTIzNDU2Nzg5XCIsXCJ1c2VybmFtZVwiOlwieGlhb21pbmdcIn0iLCJpc3MiOiJzeXN0ZW0iLCJpYXQiOjE2OTcyNzkzNTEsImV4cCI6MTY5NzI4MTE1MX0.8HbdftjIZMxJa7sMfgtqOwWMKX_d04KzVDbyYFAm9XU";
        Claims claims = jwtUtil.parseToken(token);

    }
    @Test
    public void testParseJwt2(){
        String token = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJmNWY4Nzc4Yy02NWRjLTQyYWEtOWM4Yi02MTEyOGQ1ZmQwZTMiLCJzdWIiOiJ7XCJwaG9uZVwiOlwiMTIzNDU2Nzg5XCIsXCJ1c2VybmFtZVwiOlwieGlhb21pbmdcIn0iLCJpc3MiOiJzeXN0ZW0iLCJpYXQiOjE2OTcyNzkzNTEsImV4cCI6MTY5NzI4MTE1MX0.8HbdftjIZMxJa7sMfgtqOwWMKX_d04KzVDbyYFAm9XU";
        User user = jwtUtil.parseToken(token,User.class);
        System.out.println(user);

    }
    //测试注册
    @Test
    public void testRegister() {
        User user = new User();
        user.setUsername("xiaoming1");
        user.setPassword("123456");
        user.setPhone("123456789");
        String token = jwtUtil.createToken(user);
        System.out.println(token);
    }
}
