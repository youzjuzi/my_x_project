package com.diy.common.utils;

import com.alibaba.fastjson2.JSON;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtBuilder;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Date;
import java.util.UUID;

@Component
public class JwtUtil {
    // 有效期
    private static final long JWT_EXPIRE = 30*60*1000L;  //半小时
    // 令牌秘钥
    private static final String JWT_KEY = "123456";

    public  String createToken(Object data){
        // 当前时间
        long currentTime = System.currentTimeMillis();
        // 过期时间
        long expTime = currentTime+JWT_EXPIRE;
        // 构建jwt
        return Jwts.builder()
                .id(UUID.randomUUID().toString())
                .subject(JSON.toJSONString(data))
                .issuer("system")
                .issuedAt(new Date(currentTime))
                .expiration(new Date(expTime))
                .compact();
    }

//    private SecretKey encodeSecret(String key){
//        byte[] encode = Base64.getEncoder().encode(key.getBytes());
//        SecretKeySpec aes = new SecretKeySpec(encode, 0, encode.length, "AES");
//        return  aes;
//    }
    private SecretKey generateKey() {
        byte[] keyBytes = JWT_KEY.getBytes(StandardCharsets.UTF_8);
        return Keys.hmacShaKeyFor(keyBytes);
    }

    public  Claims parseToken(String token){
        return Jwts.parser()
                .verifyWith(generateKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    public <T> T parseToken(String token,Class<T> clazz){
        Claims claims = parseToken(token);
        return JSON.parseObject(claims.getSubject(), clazz);
    }

}
