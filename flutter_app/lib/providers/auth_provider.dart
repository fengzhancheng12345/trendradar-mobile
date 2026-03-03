import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class AuthProvider extends ChangeNotifier {
  final ApiService _api = apiService;
  
  bool _isLoading = false;
  bool _isLoggedIn = false;
  String? _username;
  String? _email;
  bool _isVip = false;
  int _keywordsCount = 1;

  bool get isLoading => _isLoading;
  bool get isLoggedIn => _isLoggedIn;
  String? get username => _username;
  String? get email => _email;
  bool get isVip => _isVip;
  int get keywordsCount => _keywordsCount;

  AuthProvider() {
    _checkLogin();
  }

  Future<void> _checkLogin() async {
    _isLoading = true;
    notifyListeners();

    await _api.loadTokens();
    
    if (_api._accessToken != null) {
      try {
        final response = await _api.getProfile();
        if (response.statusCode == 200) {
          _isLoggedIn = true;
          _username = response.data['username'];
          _email = response.data['email'];
          _isVip = response.data['is_vip'] ?? false;
          _keywordsCount = response.data['keywords_count'] ?? 1;
        }
      } catch (e) {
        await _api.clearTokens();
      }
    }

    _isLoading = false;
    notifyListeners();
  }

  Future<bool> login(String username, String password) async {
    _isLoading = true;
    notifyListeners();

    try {
      await _api.login(username, password);
      
      final response = await _api.getProfile();
      if (response.statusCode == 200) {
        _isLoggedIn = true;
        _username = response.data['username'];
        _email = response.data['email'];
        _isVip = response.data['is_vip'] ?? false;
        _keywordsCount = response.data['keywords_count'] ?? 1;
        
        _isLoading = false;
        notifyListeners();
        return true;
      }
    } catch (e) {
      // 登录失败
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }

  Future<bool> register(String username, String password, {String? email}) async {
    _isLoading = true;
    notifyListeners();

    try {
      await _api.register(username, password, email: email);
      
      // 注册成功后自动登录
      return await login(username, password);
    } catch (e) {
      // 注册失败
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }

  Future<void> logout() async {
    await _api.logout();
    _isLoggedIn = false;
    _username = null;
    _email = null;
    _isVip = false;
    _keywordsCount = 1;
    notifyListeners();
  }

  Future<void> refreshProfile() async {
    if (!_isLoggedIn) return;
    
    try {
      final response = await _api.getProfile();
      if (response.statusCode == 200) {
        _isVip = response.data['is_vip'] ?? false;
        _keywordsCount = response.data['keywords_count'] ?? 1;
        notifyListeners();
      }
    } catch (e) {
      // 刷新失败
    }
  }
}
