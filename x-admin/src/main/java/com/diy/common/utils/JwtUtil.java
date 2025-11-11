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
    private static final String JWT_KEY = "YourSuperSecretKeyForHS256Algorithm123";

    // 将密钥字符串转换为SecretKey对象，并作为静态常量，确保全局唯一且只生成一次
    private static final SecretKey SECRET_KEY = Keys.hmacShaKeyFor(JWT_KEY.getBytes(StandardCharsets.UTF_8));

    /**
     * 创建JWT Token
     * @param data
     * @return
     */
    public String createToken(Object data) {
        long currentTime = System.currentTimeMillis();
        long expTime = currentTime + JWT_EXPIRE;

        return Jwts.builder()
                .id(UUID.randomUUID().toString())
                .subject(JSON.toJSONString(data))
                .issuer("system")
                .issuedAt(new Date(currentTime))
                .expiration(new Date(expTime))
                .signWith(SECRET_KEY, SignatureAlgorithm.HS256)
                .compact();
    }
    /**
     * 解析JWT Token
     * @param token
     * @return
     */
    public  Claims parseToken(String token){
        return Jwts.parser()
                .verifyWith(SECRET_KEY)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    /**
     * 解析Token并转换为指定对象
     * @param token
     * @param clazz
     * @param <T>
     * @return
     */
    public <T> T parseToken(String token,Class<T> clazz){
        Claims claims = parseToken(token);
        return JSON.parseObject(claims.getSubject(), clazz);
    }
}
