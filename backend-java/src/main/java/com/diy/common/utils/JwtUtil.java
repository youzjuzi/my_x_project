package com.diy.common.utils;

import com.alibaba.fastjson2.JSON;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.UUID;

@Component
public class JwtUtil {
    // 有效期
    //private static final long JWT_EXPIRE = 30*60*1000L;  //半小时
    //由于加入了redis,jwt验证设置一天时间
    private static final long JWT_EXPIRE = 1*24*60*60*1000L;  //1天
    private final SecretKey secretKey;

    public JwtUtil(@Value("${jwt.secret}") String jwtKey) {
        this.secretKey = Keys.hmacShaKeyFor(jwtKey.getBytes(StandardCharsets.UTF_8));
    }

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
                .signWith(secretKey, SignatureAlgorithm.HS256)
                .compact();
    }
    /**
     * 解析JWT Token
     * @param token
     * @return
     */
    public  Claims parseToken(String token){
        return Jwts.parser()
                .verifyWith(secretKey)
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
