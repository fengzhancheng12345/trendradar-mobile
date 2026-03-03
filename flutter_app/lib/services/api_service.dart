import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api/v1';
  
  late final Dio _dio;
  String? _accessToken;
  String? _refreshToken;

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      headers: {
        'Content-Type': 'application/json',
      },
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (_accessToken != null) {
          options.headers['Authorization'] = 'Bearer $_accessToken';
        }
        return handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          final refreshed = await _refreshToken();
          if (refreshed) {
            final opts = error.requestOptions;
            opts.headers['Authorization'] = 'Bearer $_accessToken';
            final response = await _dio.fetch(opts);
            return handler.resolve(response);
          }
        }
        return handler.next(error);
      },
    ));
  }

  Future<void> loadTokens() async {
    final prefs = await SharedPreferences.getInstance();
    _accessToken = prefs.getString('access_token');
    _refreshToken = prefs.getString('refresh_token');
  }

  Future<void> saveTokens(String access, String refresh) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', access);
    await prefs.setString('refresh_token', refresh);
    _accessToken = access;
    _refreshToken = refresh;
  }

  Future<void> clearTokens() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    _accessToken = null;
    _refreshToken = null;
  }

  Future<bool> _refreshToken() async {
    if (_refreshToken == null) return false;
    
    try {
      final response = await _dio.post(
        '/auth/refresh',
        data: {'refresh_token': _refreshToken},
      );
      
      if (response.statusCode == 200) {
        await saveTokens(
          response.data['access_token'],
          response.data['refresh_token'],
        );
        return true;
      }
    } catch (e) {
      await clearTokens();
    }
    return false;
  }

  // Auth APIs
  Future<Response> register(String username, String password, {String? email}) async {
    return await _dio.post('/auth/register', data: {
      'username': username,
      'password': password,
      'email': email,
    });
  }

  Future<Response> login(String username, String password) async {
    final response = await _dio.post(
      '/auth/login',
      data: FormData.fromMap({
        'username': username,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      await saveTokens(
        response.data['access_token'],
        response.data['refresh_token'],
      );
    }
    return response;
  }

  Future<void> logout() async {
    await clearTokens();
  }

  Future<Response> getProfile() async {
    return await _dio.get('/auth/profile');
  }

  // Trending APIs
  Future<Response> getTrending({String? platform, String? keywords}) async {
    return await _dio.get('/trending', queryParameters: {
      if (platform != null) 'platform': platform,
      if (keywords != null) 'keywords': keywords,
    });
  }

  Future<Response> getPlatforms() async {
    return await _dio.get('/trending/platforms');
  }

  Future<Response> getHistory({String? platform, int days = 7}) async {
    return await _dio.get('/trending/history', queryParameters: {
      if (platform != null) 'platform': platform,
      'days': days,
    });
  }

  // VIP APIs (支付宝当面付)
  Future<Response> getVipStatus() async {
    return await _dio.get('/vip/status');
  }

  Future<Response> getVipProducts() async {
    return await _dio.get('/vip/products');
  }

  /// 创建支付宝当面付订单
  /// [durationDays] VIP时长 (30/90/180/365天)
  Future<Response> createPayOrder(int durationDays) async {
    return await _dio.post('/vip/pay', data: {
      'duration_days': durationDays,
    });
  }

  /// 检查支付状态 (轮询)
  Future<Response> checkPayment(String orderNo) async {
    return await _dio.post('/vip/check', data: {'order_no': orderNo});
  }

  /// 取消订单
  Future<Response> cancelOrder(String orderNo) async {
    return await _dio.post('/vip/cancel', data: {'order_no': orderNo});
  }

  // AI APIs
  Future<Response> analyzeTopics(List<String> topics) async {
    return await _dio.post('/ai/analyze', data: {
      'topics': topics,
      'analysis_type': 'summary',
    });
  }

  Future<Response> translate(String text, String targetLang) async {
    return await _dio.post('/ai/translate', data: {
      'text': text,
      'target_lang': targetLang,
    });
  }
}

final apiService = ApiService();
